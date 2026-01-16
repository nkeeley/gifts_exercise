"""
Pytest configuration and shared fixtures for backend tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


@pytest.fixture
def client():
    """
    Create a test client for FastAPI application.
    
    Returns:
        TestClient instance for making HTTP requests to the API
    """
    return TestClient(app)


@pytest.fixture
def sample_transaction_data():
    """
    Create sample transaction data for testing.
    
    Returns:
        DataFrame with sample transaction records including edge cases
    """
    base_date = datetime(2023, 1, 1)
    
    data = {
        "Invoice": ["INV001", "INV001", "INV002", "INV003", "INV004", "INV005", "INV006"],
        "StockCode": ["PROD001", "PROD002", "PROD001", "PROD003", "PROD001", "PROD002", "PROD004"],
        "Description": ["Product 1", "Product 2", "Product 1", "Product 3", "Product 1", "Product 2", "Product 4"],
        "Quantity": [5, 3, 2, 10, 1, 4, 0],  # Includes zero quantity
        "InvoiceDate": [
            base_date,
            base_date,
            base_date + timedelta(days=30),
            base_date + timedelta(days=60),
            base_date + timedelta(days=90),
            base_date + timedelta(days=120),
            base_date + timedelta(days=150)
        ],
        "Price": [10.0, 15.0, 10.0, 20.0, 10.0, 15.0, 5.0],
        "Customer ID": [12345.0, 12345.0, 12345.0, 12345.0, 12345.0, 12345.0, 67890.0],
        "Country": ["UK", "UK", "UK", "UK", "UK", "UK", "US"]
    }
    
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def sample_transaction_data_with_nulls():
    """
    Create sample transaction data with null values for testing null handling.
    
    Returns:
        DataFrame with null values in critical columns
    """
    base_date = datetime(2023, 1, 1)
    
    data = {
        "Invoice": ["INV001", "INV002", "INV003"],
        "StockCode": ["PROD001", "PROD002", "PROD003"],
        "Description": ["Product 1", "Product 2", "Product 3"],
        "Quantity": [5, 3, 2],
        "InvoiceDate": [base_date, base_date + timedelta(days=30), base_date + timedelta(days=60)],
        "Price": [10.0, 15.0, 20.0],
        "Customer ID": [12345.0, None, 12345.0],  # One null customer ID
        "Country": ["UK", "UK", "UK"]
    }
    
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def sample_transaction_data_with_negatives():
    """
    Create sample transaction data with negative values (refunds).
    
    Returns:
        DataFrame with negative prices and quantities
    """
    base_date = datetime(2023, 1, 1)
    
    data = {
        "Invoice": ["INV001", "INV002", "INV003"],
        "StockCode": ["PROD001", "PROD002", "PROD003"],
        "Description": ["Product 1", "Product 2", "Product 3"],
        "Quantity": [5, -2, 3],  # Negative quantity (refund)
        "InvoiceDate": [base_date, base_date + timedelta(days=30), base_date + timedelta(days=60)],
        "Price": [10.0, -15.0, 20.0],  # Negative price (refund)
        "Customer ID": [12345.0, 12345.0, 12345.0],
        "Country": ["UK", "UK", "UK"]
    }
    
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def sample_parquet_file(sample_transaction_data, tmp_path):
    """
    Create a temporary parquet file with sample data.
    
    Args:
        sample_transaction_data: Fixture providing sample DataFrame
        tmp_path: Pytest temporary directory fixture
    
    Returns:
        Path to temporary parquet file
    """
    parquet_path = tmp_path / "test_data.parquet"
    sample_transaction_data.to_parquet(parquet_path, engine="fastparquet", index=False)
    return str(parquet_path)


@pytest.fixture
def sample_parquet_file_with_nulls(sample_transaction_data_with_nulls, tmp_path):
    """
    Create a temporary parquet file with null values.
    
    Args:
        sample_transaction_data_with_nulls: Fixture providing DataFrame with nulls
        tmp_path: Pytest temporary directory fixture
    
    Returns:
        Path to temporary parquet file
    """
    parquet_path = tmp_path / "test_data_nulls.parquet"
    sample_transaction_data_with_nulls.to_parquet(parquet_path, engine="fastparquet", index=False)
    return str(parquet_path)


@pytest.fixture
def sample_customer_record():
    """
    Create a sample customer record for testing.
    
    Returns:
        Dictionary representing a customer record
    """
    return {
        "customer_id": 12345.0,
        "recency": 30,
        "frequency": 5,
        "monetary": 1250.50,
        "median_purchase_days": 15.0,
        "churn_ratio": 2.0,
        "churn_label": "High Risk",
        "monetary_log": 7.13,
        "cluster_assignment": 1,
        "segment": "Monthly, High-Value Buyers"
    }


@pytest.fixture
def sample_customer_record_with_nulls():
    """
    Create a sample customer record with null values for testing.
    
    Returns:
        Dictionary representing a customer record with null churn_ratio and churn_label
    """
    return {
        "customer_id": 67890.0,
        "recency": 0,
        "frequency": 1,
        "monetary": 100.0,
        "median_purchase_days": 0.0,
        "churn_ratio": None,  # Will be inf/NaN due to division by zero
        "churn_label": None,
        "monetary_log": 4.61,
        "cluster_assignment": 2,
        "segment": "Experimental / Hesitant, Lower-Value Buyers"
    }


@pytest.fixture
def clear_cache():
    """
    Clear the customer cache before and after each test.
    
    Yields:
        None, but ensures cache is cleared before and after test
    """
    from main import _customer_cache
    _customer_cache.clear()
    yield
    _customer_cache.clear()
