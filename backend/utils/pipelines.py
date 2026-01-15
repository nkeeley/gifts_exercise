"""
Data processing pipeline for gifts exercise.

This module contains functions for ingesting, transforming, and processing
retail transaction data to create customer segmentation models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def ingest_data(data_path: str) -> pd.DataFrame:
    """
    Load raw transaction data from parquet file.
    
    Args:
        data_path: Path to the parquet file containing raw transaction data.
                   Should be relative to the backend directory or absolute path.
    
    Returns:
        DataFrame containing raw transaction data with columns:
        - Invoice: Invoice number
        - StockCode: Product stock code
        - Description: Product description
        - Quantity: Quantity purchased
        - InvoiceDate: Date and time of invoice
        - Price: Unit price
        - Customer ID: Customer identifier
        - Country: Country of purchase
    """
    raw_df = pd.read_parquet(data_path, engine="fastparquet")
    return raw_df


def transform_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform raw transaction data.
    
    Removes invalid records (negative prices/quantities) and records
    with missing customer IDs.
    
    Args:
        raw_df: Raw transaction DataFrame from ingest_data()
    
    Returns:
        Cleaned DataFrame with valid transactions only.
    """
    # Remove negative prices and quantities (likely refunds)
    # Drop rows with null Customer ID
    full_df = raw_df[
        (raw_df["Price"] >= 0) & (raw_df["Quantity"] >= 0)
    ].dropna(subset=["Customer ID"])
    
    return full_df


def add_features(full_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Add derived features and create customer-level aggregations.
    
    Creates invoice-level and customer-level DataFrames with RFM metrics
    (Recency, Frequency, Monetary) and customer segmentation.
    
    Args:
        full_df: Cleaned transaction DataFrame from transform_data()
    
    Returns:
        Tuple of three DataFrames:
        - full_df: Original DataFrame with added lineitem_amount column
        - invoice_df: Invoice-level aggregations with interpurchase days
        - customer_df: Customer-level aggregations with RFM metrics and segments
    """
    # Add line item amount feature
    full_df = full_df.copy()
    full_df["lineitem_amount"] = full_df["Quantity"] * full_df["Price"]
    
    # Get max date as reference for 'today'
    max_date = full_df["InvoiceDate"].max().normalize()
    
    # Create invoice-level DataFrame
    invoice_df = (
        full_df
        .assign(InvoiceDate=full_df["InvoiceDate"].dt.normalize())
        .groupby(["Customer ID", "InvoiceDate"], as_index=False)
        .agg(
            monetary=("lineitem_amount", "sum")
        )
    )
    
    # Sort by customer, then date to help calculate interpurchase days
    invoice_df = invoice_df.sort_values(["Customer ID", "InvoiceDate"])
    
    # Calculate days between purchases
    invoice_df["days_between_purchases"] = (
        invoice_df
        .groupby("Customer ID")["InvoiceDate"]
        .diff()
        .dt.days
    )
    
    # Create customer-level DataFrame with RFM metrics
    customer_df = (
        invoice_df
        .groupby("Customer ID")
        .agg(
            customer_id=("Customer ID", "first"),
            # Recency: days since most recent invoice
            recency=("InvoiceDate", lambda x: (max_date - x.max().normalize()).days),
            # Frequency: number of invoices
            frequency=("InvoiceDate", "count"),
            # Monetary: total spend
            monetary=("monetary", "sum"),
            # Median days between purchases
            median_purchase_days=("days_between_purchases", "median")
        )
        .reset_index(drop=True)
    )
    
    # Fill NaN median_purchase_days with recency (for customers with only one purchase)
    customer_df["median_purchase_days"] = (
        customer_df["median_purchase_days"]
        .fillna(customer_df["recency"])
    )
    
    # Add churn ratio feature
    customer_df["churn_ratio"] = customer_df["recency"] / customer_df["median_purchase_days"]
    
    # Add churn label based on churn_ratio
    def assign_churn_label(ratio):
        """Assign churn risk label based on churn ratio."""
        if pd.isna(ratio) or not np.isfinite(ratio):
            return None
        if ratio <= 1:
            return "Low Risk"
        elif ratio < 2:
            return "Medium Risk"
        else:  # ratio >= 2
            return "High Risk"
    
    customer_df["churn_label"] = customer_df["churn_ratio"].apply(assign_churn_label)
    
    # Add customer segmentation using KMeans clustering
    customer_df = _add_segmentation(customer_df)
    
    return full_df, invoice_df, customer_df


def _add_segmentation(customer_df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    Add customer segmentation using KMeans clustering on RFM features.
    
    Clusters customers based on normalized Recency, Frequency, and Monetary
    (log-transformed) values, then assigns segment names.
    
    Args:
        customer_df: Customer-level DataFrame with RFM metrics
        n_clusters: Number of clusters for KMeans (default: 3)
    
    Returns:
        Customer DataFrame with added 'monetary_log', 'cluster_assignment', 
        and 'segment' columns.
    """
    customer_df = customer_df.copy()
    
    # Log transform monetary for clustering (to handle skewness)
    customer_df['monetary_log'] = np.log1p(customer_df['monetary'])
    
    # Prepare features for clustering
    kmeans_df = customer_df[["recency", "frequency", "monetary_log"]]
    
    # Normalize the data
    scaler = StandardScaler()
    X = scaler.fit_transform(kmeans_df)
    
    # Fit KMeans clustering
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )
    
    result = kmeans.fit_predict(X)
    
    # Add cluster assignments
    customer_df["cluster_assignment"] = result
    
    # Map clusters to segment names
    cluster_map = {
        0: 'Seasonal Buyers',
        1: 'Monthly, High-Value Buyers',
        2: 'Experimental / Hesitant, Lower-Value Buyers'
    }
    
    # Handle case where n_clusters might be different
    if n_clusters == 3:
        customer_df['segment'] = customer_df['cluster_assignment'].map(cluster_map)
    else:
        # For other cluster counts, use generic names
        customer_df['segment'] = customer_df['cluster_assignment'].apply(
            lambda x: f'Segment {x}'
        )
    
    return customer_df


def output_data(
    full_df: pd.DataFrame,
    invoice_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    output_dir: str = "data/processed"
) -> None:
    """
    Save processed DataFrames to CSV files.
    
    Args:
        full_df: Full transaction DataFrame with features
        invoice_df: Invoice-level aggregated DataFrame
        customer_df: Customer-level aggregated DataFrame with segments
        output_dir: Directory path (relative to backend or absolute) where
                   CSV files will be saved. Defaults to "data/processed".
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV files
    customer_df.to_csv(output_path / "customer_df.csv", index=False)
    invoice_df.to_csv(output_path / "invoice_df.csv", index=False)
    full_df.to_csv(output_path / "full_df.csv", index=False)


def run_full_pipeline(
    data_path: str,
    output_dir: str = "data/processed"
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run the complete data processing pipeline from ingestion to output.
    
    This function orchestrates all pipeline steps:
    1. Ingest raw data
    2. Transform and clean data
    3. Add features and create aggregations
    4. Save results to CSV files
    
    Args:
        data_path: Path to the input parquet file
        output_dir: Directory path for output CSV files
    
    Returns:
        Tuple of (full_df, invoice_df, customer_df) DataFrames
    """
    # Step 1: Ingest data
    raw_df = ingest_data(data_path)
    
    # Step 2: Transform data
    full_df = transform_data(raw_df)
    
    # Step 3: Add features
    full_df, invoice_df, customer_df = add_features(full_df)
    
    # Step 4: Output data
    output_data(full_df, invoice_df, customer_df, output_dir)
    
    return full_df, invoice_df, customer_df


if __name__ == "__main__":
    # Example usage
    data_path = "../data/raw/online_retail.parquet"
    output_dir = "../data/processed"
    
    full_df, invoice_df, customer_df = run_full_pipeline(data_path, output_dir)
    
    print(f"Pipeline completed successfully!")
    print(f"Full DF shape: {full_df.shape}")
    print(f"Invoice DF shape: {invoice_df.shape}")
    print(f"Customer DF shape: {customer_df.shape}")
    print(customer_df.head().to_string())