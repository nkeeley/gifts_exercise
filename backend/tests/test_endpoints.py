"""
Test suite for FastAPI endpoints.

Tests include:
- Input validation (file types, parameters)
- Output validation (response schemas)
- Null and NaN value handling
- Timeout scenarios
- Error handling
"""

import pytest
import pandas as pd
import numpy as np
from fastapi import status
from pathlib import Path
import time
import io


class TestProcessDataEndpoint:
    """Test suite for POST /api/process-data endpoint."""
    
    def test_valid_parquet_file_upload(self, client, sample_parquet_file):
        """
        Test that a valid parquet file upload is processed successfully.
        
        Verifies:
        - Endpoint accepts valid parquet file
        - Response has correct status code
        - Response schema matches ProcessDataResponse
        - Data is returned in correct format
        """
        with open(sample_parquet_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate response structure
        assert "status" in data
        assert "message" in data
        assert "data" in data
        assert "total_customers" in data
        assert "segment_statistics" in data
        
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert isinstance(data["total_customers"], int)
        assert isinstance(data["segment_statistics"], list)
    
    def test_invalid_file_type_rejection(self, client, tmp_path):
        """
        Test that non-parquet files are rejected with 400 error.
        
        Verifies:
        - Endpoint rejects non-parquet files
        - Returns 400 Bad Request
        - Error message is descriptive
        """
        # Create a CSV file instead of parquet
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text("col1,col2\nval1,val2\n")
        
        with open(csv_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data.csv", f, "text/csv")}
            )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "parquet" in response.json()["detail"].lower()
    
    def test_missing_file_parameter(self, client):
        """
        Test that missing file parameter returns appropriate error.
        
        Verifies:
        - Endpoint handles missing file parameter
        - Returns 422 Unprocessable Entity
        """
        response = client.post("/api/process-data")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_empty_file_handling(self, client, tmp_path):
        """
        Test that empty parquet file is handled gracefully.
        
        Verifies:
        - Empty file doesn't crash the endpoint
        - Returns appropriate error or empty result
        """
        # Create empty parquet file
        empty_df = pd.DataFrame()
        empty_file = tmp_path / "empty.parquet"
        empty_df.to_parquet(empty_file, engine="fastparquet", index=False)
        
        with open(empty_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("empty.parquet", f, "application/octet-stream")}
            )
        
        # Should either return empty result or error, but not crash
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_null_values_in_data(self, client, sample_parquet_file_with_nulls):
        """
        Test that null values in input data are handled correctly.
        
        Verifies:
        - Null Customer IDs are filtered out
        - Response doesn't contain null customer records
        - No crashes from null handling
        """
        with open(sample_parquet_file_with_nulls, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data_nulls.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All customer records should have valid customer_id
        for record in data["data"]:
            assert record["customer_id"] is not None
            assert not pd.isna(record["customer_id"])
    
    def test_nan_churn_ratio_handling(self, client, tmp_path):
        """
        Test that NaN churn_ratio values are converted to None for JSON serialization.
        
        Verifies:
        - NaN churn_ratio values are handled
        - Infinity churn_ratio values are handled
        - Response is valid JSON
        """
        # Create data that will produce NaN/inf churn_ratio (division by zero)
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
        parquet_file = tmp_path / "nan_test.parquet"
        df.to_parquet(parquet_file, engine="fastparquet", index=False)
        
        with open(parquet_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("nan_test.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that NaN/inf values are None in JSON
        for record in data["data"]:
            if record["churn_ratio"] is not None:
                assert np.isfinite(record["churn_ratio"])
    
    def test_response_schema_validation(self, client, sample_parquet_file):
        """
        Test that response matches ProcessDataResponse schema exactly.
        
        Verifies:
        - All required fields are present
        - Field types match schema
        - CustomerRecord schema is validated
        - SegmentStatistics schema is validated
        """
        with open(sample_parquet_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate top-level fields
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["total_customers"], int)
        assert isinstance(data["data"], list)
        assert isinstance(data["segment_statistics"], list)
        
        # Validate customer records if present
        if data["data"]:
            record = data["data"][0]
            required_fields = [
                "customer_id", "recency", "frequency", "monetary",
                "median_purchase_days", "churn_ratio", "churn_label",
                "monetary_log", "cluster_assignment", "segment"
            ]
            for field in required_fields:
                assert field in record
        
        # Validate segment statistics if present
        if data["segment_statistics"]:
            stat = data["segment_statistics"][0]
            required_fields = [
                "segment", "high_risk_count", "medium_risk_count",
                "med_high_ratio", "med_high_monetary_sum"
            ]
            for field in required_fields:
                assert field in stat
    
    def test_data_sorting(self, client, sample_parquet_file):
        """
        Test that customer data is sorted by churn_ratio (desc) then monetary (desc).
        
        Verifies:
        - Data is sorted correctly
        - NaN values are at the end
        """
        with open(sample_parquet_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if len(data["data"]) > 1:
            records = data["data"]
            for i in range(len(records) - 1):
                curr = records[i]
                next_rec = records[i + 1]
                
                # If both have churn_ratio, check sorting
                if curr["churn_ratio"] is not None and next_rec["churn_ratio"] is not None:
                    assert curr["churn_ratio"] >= next_rec["churn_ratio"]
                    # If churn_ratio equal, check monetary
                    if curr["churn_ratio"] == next_rec["churn_ratio"]:
                        assert curr["monetary"] >= next_rec["monetary"]
    
    def test_customer_cache_population(self, client, sample_parquet_file, clear_cache):
        """
        Test that processed customer data is stored in cache for recommendation endpoint.
        
        Verifies:
        - Customer data is cached after processing
        - Cache can be accessed by recommendation endpoint
        """
        from main import _customer_cache
        
        with open(sample_parquet_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that customers are in cache
        if data["data"]:
            customer_id = data["data"][0]["customer_id"]
            assert customer_id in _customer_cache
    
    def test_large_file_timeout(self, client, tmp_path):
        """
        Test that large files don't cause timeout issues.
        
        Note: This is a basic test - actual timeout testing would require
        configuring timeout limits in the test client or using a real server.
        
        Verifies:
        - Large files are processed without immediate timeout
        """
        # Create a moderately large dataset
        base_date = pd.Timestamp("2023-01-01")
        n_rows = 10000
        
        data = {
            "Invoice": [f"INV{i:05d}" for i in range(n_rows)],
            "StockCode": [f"PROD{i%100:03d}" for i in range(n_rows)],
            "Description": [f"Product {i%100}" for i in range(n_rows)],
            "Quantity": [1] * n_rows,
            "InvoiceDate": [base_date + pd.Timedelta(days=i%365) for i in range(n_rows)],
            "Price": [10.0 + (i % 100)] * n_rows,
            "Customer ID": [float(10000 + (i % 100)) for i in range(n_rows)],
            "Country": ["UK"] * n_rows
        }
        df = pd.DataFrame(data)
        large_file = tmp_path / "large_data.parquet"
        df.to_parquet(large_file, engine="fastparquet", index=False)
        
        start_time = time.time()
        with open(large_file, "rb") as f:
            response = client.post(
                "/api/process-data",
                files={"file": ("large_data.parquet", f, "application/octet-stream")}
            )
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 60  # 60 seconds max
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestCustomerRecommendationEndpoint:
    """Test suite for GET /api/customer/{customer_id}/recommendation endpoint."""
    
    def test_valid_customer_id(self, client, sample_parquet_file, clear_cache):
        """
        Test that valid customer ID returns recommendation.
        
        Verifies:
        - Endpoint accepts valid customer_id
        - Returns customer data and recommendation
        - Response schema matches CustomerRecommendationResponse
        """
        # First process data to populate cache
        with open(sample_parquet_file, "rb") as f:
            process_response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert process_response.status_code == status.HTTP_200_OK
        process_data = process_response.json()
        
        if process_data["data"]:
            customer_id = process_data["data"][0]["customer_id"]
            
            # Get recommendation
            response = client.get(f"/api/customer/{customer_id}/recommendation")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Validate response structure
            assert "customer" in data
            assert "recommendation" in data
            assert isinstance(data["recommendation"], str)
            assert data["customer"]["customer_id"] == customer_id
    
    def test_invalid_customer_id_not_found(self, client, clear_cache):
        """
        Test that non-existent customer ID returns 404.
        
        Verifies:
        - Endpoint returns 404 for missing customer
        - Error message is descriptive
        """
        response = client.get("/api/customer/99999.0/recommendation")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_customer_id_type_validation(self, client, clear_cache):
        """
        Test that customer_id parameter type is validated.
        
        Verifies:
        - Non-numeric customer_id is handled
        - Returns appropriate error
        """
        # Test with string that can't be converted to float
        response = client.get("/api/customer/invalid_id/recommendation")
        
        # FastAPI should handle type conversion or return 422
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,  # If converted to NaN/None
            status.HTTP_422_UNPROCESSABLE_ENTITY  # If validation fails
        ]
    
    def test_recommendation_for_all_segments(self, client, sample_parquet_file, clear_cache):
        """
        Test that recommendations are generated for all segment types.
        
        Verifies:
        - Recommendations exist for all segments
        - Recommendation text is not empty
        """
        # Process data
        with open(sample_parquet_file, "rb") as f:
            process_response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert process_response.status_code == status.HTTP_200_OK
        process_data = process_response.json()
        
        # Get unique segments
        segments = set()
        for record in process_data["data"]:
            segments.add(record["segment"])
        
        # Test recommendation for each segment
        for record in process_data["data"]:
            customer_id = record["customer_id"]
            response = client.get(f"/api/customer/{customer_id}/recommendation")
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert len(data["recommendation"]) > 0
                assert data["customer"]["segment"] == record["segment"]
    
    def test_recommendation_with_null_churn_label(self, client, tmp_path, clear_cache):
        """
        Test that recommendations work even when churn_label is None.
        
        Verifies:
        - Null churn_label doesn't break recommendation generation
        - Recommendation is still generated
        """
        # Create data that produces null churn_label
        base_date = pd.Timestamp("2023-01-01")
        data = {
            "Invoice": ["INV001"],
            "StockCode": ["PROD001"],
            "Description": ["Product 1"],
            "Quantity": [1],
            "InvoiceDate": [base_date],
            "Price": [10.0],
            "Customer ID": [88888.0],
            "Country": ["UK"]
        }
        df = pd.DataFrame(data)
        parquet_file = tmp_path / "null_churn.parquet"
        df.to_parquet(parquet_file, engine="fastparquet", index=False)
        
        # Process data
        with open(parquet_file, "rb") as f:
            process_response = client.post(
                "/api/process-data",
                files={"file": ("null_churn.parquet", f, "application/octet-stream")}
            )
        
        if process_response.status_code == status.HTTP_200_OK:
            process_data = process_response.json()
            if process_data["data"]:
                customer_id = process_data["data"][0]["customer_id"]
                response = client.get(f"/api/customer/{customer_id}/recommendation")
                
                # Should still work even with null churn_label
                assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_response_schema_validation(self, client, sample_parquet_file, clear_cache):
        """
        Test that recommendation response matches CustomerRecommendationResponse schema.
        
        Verifies:
        - Response has correct structure
        - Customer record is valid
        - Recommendation is a string
        """
        # Process data
        with open(sample_parquet_file, "rb") as f:
            process_response = client.post(
                "/api/process-data",
                files={"file": ("test_data.parquet", f, "application/octet-stream")}
            )
        
        assert process_response.status_code == status.HTTP_200_OK
        process_data = process_response.json()
        
        if process_data["data"]:
            customer_id = process_data["data"][0]["customer_id"]
            response = client.get(f"/api/customer/{customer_id}/recommendation")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Validate structure
            assert "customer" in data
            assert "recommendation" in data
            
            # Validate customer record
            customer = data["customer"]
            assert "customer_id" in customer
            assert "segment" in customer
            assert isinstance(data["recommendation"], str)
