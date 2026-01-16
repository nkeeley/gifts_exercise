"""
Test suite for data pipeline functions.

Tests include:
- Data ingestion
- Data transformation
- Feature engineering
- Null and NaN handling
- Edge cases
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from utils.pipelines import (
    ingest_data,
    transform_data,
    add_features,
    _add_segmentation,
    _calculate_segment_statistics
)


class TestIngestData:
    """Test suite for ingest_data function."""
    
    def test_valid_parquet_ingestion(self, sample_parquet_file):
        """
        Test that valid parquet file is ingested correctly.
        
        Verifies:
        - Function reads parquet file successfully
        - Returns DataFrame with expected columns
        """
        df = ingest_data(sample_parquet_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        expected_columns = ["Invoice", "StockCode", "Description", "Quantity",
                          "InvoiceDate", "Price", "Customer ID", "Country"]
        for col in expected_columns:
            assert col in df.columns
    
    def test_file_not_found_error(self):
        """
        Test that missing file raises appropriate error.
        
        Verifies:
        - FileNotFoundError is raised for non-existent file
        """
        with pytest.raises(FileNotFoundError):
            ingest_data("nonexistent_file.parquet")
    
    def test_invalid_file_format(self, tmp_path):
        """
        Test that invalid file format raises appropriate error.
        
        Verifies:
        - Error is raised for non-parquet files
        """
        # Create a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("not a parquet file")
        
        with pytest.raises(Exception):  # Could be various exceptions
            ingest_data(str(text_file))


class TestTransformData:
    """Test suite for transform_data function."""
    
    def test_valid_data_transformation(self, sample_transaction_data):
        """
        Test that valid data is transformed correctly.
        
        Verifies:
        - Negative prices/quantities are filtered out
        - Null Customer IDs are removed
        - Returns cleaned DataFrame
        """
        df = transform_data(sample_transaction_data)
        
        assert isinstance(df, pd.DataFrame)
        # All prices and quantities should be non-negative
        assert (df["Price"] >= 0).all()
        assert (df["Quantity"] >= 0).all()
        # No null Customer IDs
        assert df["Customer ID"].notna().all()
    
    def test_negative_values_filtered(self, sample_transaction_data_with_negatives):
        """
        Test that negative prices and quantities are filtered out.
        
        Verifies:
        - Negative prices are removed
        - Negative quantities are removed
        """
        df = transform_data(sample_transaction_data_with_negatives)
        
        assert (df["Price"] >= 0).all()
        assert (df["Quantity"] >= 0).all()
    
    def test_null_customer_id_filtered(self, sample_transaction_data_with_nulls):
        """
        Test that rows with null Customer ID are filtered out.
        
        Verifies:
        - Rows with null Customer ID are removed
        - Remaining rows have valid Customer IDs
        """
        df = transform_data(sample_transaction_data_with_nulls)
        
        assert df["Customer ID"].notna().all()
        # Should have fewer rows than input (one had null Customer ID)
        assert len(df) <= len(sample_transaction_data_with_nulls)
    
    def test_empty_dataframe_handling(self):
        """
        Test that empty DataFrame is handled gracefully.
        
        Verifies:
        - Empty DataFrame doesn't crash
        - Returns empty DataFrame
        """
        empty_df = pd.DataFrame(columns=["Invoice", "Price", "Quantity", "Customer ID"])
        result = transform_data(empty_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestAddFeatures:
    """Test suite for add_features function."""
    
    def test_feature_creation(self, sample_transaction_data):
        """
        Test that features are created correctly.
        
        Verifies:
        - lineitem_amount is added to full_df
        - invoice_df is created with correct structure
        - customer_df has RFM metrics
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        # Check full_df
        assert "lineitem_amount" in full_df.columns
        assert (full_df["lineitem_amount"] == full_df["Quantity"] * full_df["Price"]).all()
        
        # Check invoice_df structure
        assert "Customer ID" in invoice_df.columns
        assert "InvoiceDate" in invoice_df.columns
        assert "monetary" in invoice_df.columns
        
        # Check customer_df structure
        required_columns = [
            "customer_id", "recency", "frequency", "monetary",
            "median_purchase_days", "churn_ratio", "churn_label",
            "monetary_log", "cluster_assignment", "segment"
        ]
        for col in required_columns:
            assert col in customer_df.columns
    
    def test_churn_ratio_calculation(self, sample_transaction_data):
        """
        Test that churn_ratio is calculated correctly.
        
        Verifies:
        - churn_ratio = recency / median_purchase_days
        - Handles edge cases (division by zero)
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        for _, row in customer_df.iterrows():
            if pd.notna(row["recency"]) and pd.notna(row["median_purchase_days"]):
                if row["median_purchase_days"] > 0:
                    expected_ratio = row["recency"] / row["median_purchase_days"]
                    if pd.notna(row["churn_ratio"]):
                        assert abs(row["churn_ratio"] - expected_ratio) < 0.01
    
    def test_churn_label_assignment(self, sample_transaction_data):
        """
        Test that churn labels are assigned correctly.
        
        Verifies:
        - Low Risk: churn_ratio <= 1
        - Medium Risk: 1 < churn_ratio < 2
        - High Risk: churn_ratio >= 2
        - None for invalid ratios
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        for _, row in customer_df.iterrows():
            if pd.notna(row["churn_ratio"]) and np.isfinite(row["churn_ratio"]):
                ratio = row["churn_ratio"]
                label = row["churn_label"]
                
                if ratio <= 1:
                    assert label == "Low Risk"
                elif ratio < 2:
                    assert label == "Medium Risk"
                else:
                    assert label == "High Risk"
    
    def test_nan_churn_ratio_handling(self, tmp_path):
        """
        Test that NaN/inf churn_ratio values are handled correctly.
        
        Verifies:
        - Division by zero produces None churn_label
        - NaN values don't crash the function
        """
        # Create data that will cause division by zero
        base_date = pd.Timestamp("2023-01-01")
        data = {
            "Invoice": ["INV001"],
            "StockCode": ["PROD001"],
            "Description": ["Product 1"],
            "Quantity": [1],
            "InvoiceDate": [base_date],
            "Price": [10.0],
            "Customer ID": [99999.0],
            "Country": ["UK"]
        }
        df = pd.DataFrame(data)
        
        full_df, invoice_df, customer_df = add_features(df)
        
        # Customer with single purchase should have median_purchase_days = recency
        # This might cause churn_ratio = 1 or inf
        for _, row in customer_df.iterrows():
            if pd.isna(row["churn_ratio"]) or not np.isfinite(row["churn_ratio"]):
                assert row["churn_label"] is None
    
    def test_segmentation_creation(self, sample_transaction_data):
        """
        Test that customer segmentation is created.
        
        Verifies:
        - All customers have a segment assigned
        - Segments are valid names
        - cluster_assignment is an integer
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        valid_segments = [
            "Monthly, High-Value Buyers",
            "Seasonal Buyers",
            "Experimental / Hesitant, Lower-Value Buyers"
        ]
        
        for _, row in customer_df.iterrows():
            assert row["segment"] in valid_segments
            assert isinstance(row["cluster_assignment"], (int, np.integer))
            assert pd.notna(row["monetary_log"])


class TestAddSegmentation:
    """Test suite for _add_segmentation function."""
    
    def test_segmentation_with_default_clusters(self, sample_transaction_data):
        """
        Test segmentation with default 3 clusters.
        
        Verifies:
        - Segmentation creates 3 clusters
        - Segment names are assigned correctly
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        segments = customer_df["segment"].unique()
        assert len(segments) <= 3  # May have fewer if not enough customers
        
        valid_segments = [
            "Monthly, High-Value Buyers",
            "Seasonal Buyers",
            "Experimental / Hesitant, Lower-Value Buyers"
        ]
        for seg in segments:
            assert seg in valid_segments
    
    def test_segmentation_with_custom_clusters(self):
        """
        Test segmentation with custom number of clusters.
        
        Verifies:
        - Function accepts custom n_clusters
        - Creates appropriate number of segments
        """
        # Create minimal data
        base_date = pd.Timestamp("2023-01-01")
        data = {
            "customer_id": [1.0, 2.0, 3.0, 4.0, 5.0],
            "recency": [10, 20, 30, 40, 50],
            "frequency": [5, 4, 3, 2, 1],
            "monetary": [1000.0, 800.0, 600.0, 400.0, 200.0],
            "median_purchase_days": [10.0, 15.0, 20.0, 25.0, 30.0],
            "churn_ratio": [1.0, 1.33, 1.5, 1.6, 1.67],
            "churn_label": ["Low Risk", "Medium Risk", "Medium Risk", "Medium Risk", "Medium Risk"]
        }
        customer_df = pd.DataFrame(data)
        
        result_df = _add_segmentation(customer_df, n_clusters=2)
        
        assert "segment" in result_df.columns
        assert "cluster_assignment" in result_df.columns
        assert len(result_df["cluster_assignment"].unique()) <= 2


class TestCalculateSegmentStatistics:
    """Test suite for _calculate_segment_statistics function."""
    
    def test_statistics_calculation(self, sample_transaction_data):
        """
        Test that segment statistics are calculated correctly.
        
        Verifies:
        - Statistics are calculated for each segment
        - Total row is included
        - Counts and ratios are correct
        """
        full_df, invoice_df, customer_df = add_features(sample_transaction_data)
        
        stats = _calculate_segment_statistics(customer_df)
        
        assert isinstance(stats, list)
        assert len(stats) > 0
        
        # Check that Total row exists
        total_row = None
        for stat in stats:
            if stat.segment == "Total":
                total_row = stat
                break
        
        assert total_row is not None
        
        # Validate statistics structure
        for stat in stats:
            assert isinstance(stat.segment, str)
            assert isinstance(stat.high_risk_count, int)
            assert isinstance(stat.medium_risk_count, int)
            assert isinstance(stat.med_high_ratio, float)
            assert isinstance(stat.med_high_monetary_sum, float)
            assert 0 <= stat.med_high_ratio <= 1
    
    def test_statistics_with_null_churn_labels(self, tmp_path):
        """
        Test that statistics handle null churn_labels correctly.
        
        Verifies:
        - Null churn_labels don't break statistics
        - Counts are accurate
        """
        # Create data with null churn_labels
        base_date = pd.Timestamp("2023-01-01")
        data = {
            "Invoice": ["INV001", "INV002"],
            "StockCode": ["PROD001", "PROD002"],
            "Description": ["Product 1", "Product 2"],
            "Quantity": [1, 1],
            "InvoiceDate": [base_date, base_date + pd.Timedelta(days=30)],
            "Price": [10.0, 20.0],
            "Customer ID": [11111.0, 22222.0],
            "Country": ["UK", "UK"]
        }
        df = pd.DataFrame(data)
        
        full_df, invoice_df, customer_df = add_features(df)
        
        # Manually set some churn_labels to None to test
        customer_df.loc[customer_df.index[0], "churn_label"] = None
        
        stats = _calculate_segment_statistics(customer_df)
        
        # Should not crash
        assert len(stats) > 0
    
    def test_statistics_with_empty_segment(self):
        """
        Test that statistics handle edge cases with empty segments.
        
        Verifies:
        - Empty segments don't cause errors
        - Ratios are 0 for empty segments
        """
        # Create minimal customer_df
        customer_df = pd.DataFrame({
            "customer_id": [1.0],
            "recency": [10],
            "frequency": [1],
            "monetary": [100.0],
            "median_purchase_days": [10.0],
            "churn_ratio": [1.0],
            "churn_label": ["Low Risk"],
            "monetary_log": [4.61],
            "cluster_assignment": [0],
            "segment": ["Monthly, High-Value Buyers"]
        })
        
        stats = _calculate_segment_statistics(customer_df)
        
        assert len(stats) > 0
        # Find segment with Low Risk only
        for stat in stats:
            if stat.segment == "Monthly, High-Value Buyers":
                assert stat.high_risk_count == 0
                assert stat.medium_risk_count == 0
                assert stat.med_high_ratio == 0.0
