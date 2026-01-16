"""
Test suite for Pydantic schemas.

Tests include:
- Schema validation
- Type checking
- Optional field handling
- Edge cases
"""

import pytest
import numpy as np
from pydantic import ValidationError

from schemas import (
    CustomerRecord,
    SegmentStatistics,
    ProcessDataResponse,
    CustomerRecommendationResponse
)


class TestCustomerRecord:
    """Test suite for CustomerRecord schema."""
    
    def test_valid_customer_record(self):
        """
        Test that valid customer record passes validation.
        
        Verifies:
        - All required fields are accepted
        - Types are validated correctly
        """
        record = CustomerRecord(
            customer_id=12345.0,
            recency=30,
            frequency=5,
            monetary=1250.50,
            median_purchase_days=15.0,
            churn_ratio=2.0,
            churn_label="High Risk",
            monetary_log=7.13,
            cluster_assignment=1,
            segment="Monthly, High-Value Buyers"
        )
        
        assert record.customer_id == 12345.0
        assert record.recency == 30
        assert record.churn_label == "High Risk"
    
    def test_customer_record_with_null_churn_ratio(self):
        """
        Test that null churn_ratio is accepted.
        
        Verifies:
        - Optional churn_ratio can be None
        - Validation passes with None value
        """
        record = CustomerRecord(
            customer_id=12345.0,
            recency=30,
            frequency=5,
            monetary=1250.50,
            median_purchase_days=15.0,
            churn_ratio=None,
            churn_label=None,
            monetary_log=7.13,
            cluster_assignment=1,
            segment="Monthly, High-Value Buyers"
        )
        
        assert record.churn_ratio is None
        assert record.churn_label is None
    
    def test_customer_record_with_null_churn_label(self):
        """
        Test that null churn_label is accepted.
        
        Verifies:
        - Optional churn_label can be None
        - Validation passes with None value
        """
        record = CustomerRecord(
            customer_id=12345.0,
            recency=30,
            frequency=5,
            monetary=1250.50,
            median_purchase_days=15.0,
            churn_ratio=1.5,
            churn_label=None,
            monetary_log=7.13,
            cluster_assignment=1,
            segment="Monthly, High-Value Buyers"
        )
        
        assert record.churn_label is None
    
    def test_customer_record_missing_required_field(self):
        """
        Test that missing required fields raise ValidationError.
        
        Verifies:
        - Missing required fields cause validation error
        - Error message is descriptive
        """
        with pytest.raises(ValidationError):
            CustomerRecord(
                customer_id=12345.0,
                recency=30,
                # Missing frequency
                monetary=1250.50,
                median_purchase_days=15.0,
                churn_ratio=2.0,
                churn_label="High Risk",
                monetary_log=7.13,
                cluster_assignment=1,
                segment="Monthly, High-Value Buyers"
            )
    
    def test_customer_record_wrong_type(self):
        """
        Test that wrong field types raise ValidationError.
        
        Verifies:
        - Type validation works correctly
        - String instead of int/float raises error
        """
        with pytest.raises(ValidationError):
            CustomerRecord(
                customer_id=12345.0,
                recency="thirty",  # Should be int
                frequency=5,
                monetary=1250.50,
                median_purchase_days=15.0,
                churn_ratio=2.0,
                churn_label="High Risk",
                monetary_log=7.13,
                cluster_assignment=1,
                segment="Monthly, High-Value Buyers"
            )
    
    def test_customer_record_all_segments(self):
        """
        Test that all valid segments are accepted.
        
        Verifies:
        - All three segment types are valid
        - No validation errors for valid segments
        """
        segments = [
            "Monthly, High-Value Buyers",
            "Seasonal Buyers",
            "Experimental / Hesitant, Lower-Value Buyers"
        ]
        
        for segment in segments:
            record = CustomerRecord(
                customer_id=12345.0,
                recency=30,
                frequency=5,
                monetary=1250.50,
                median_purchase_days=15.0,
                churn_ratio=2.0,
                churn_label="High Risk",
                monetary_log=7.13,
                cluster_assignment=1,
                segment=segment
            )
            assert record.segment == segment


class TestSegmentStatistics:
    """Test suite for SegmentStatistics schema."""
    
    def test_valid_segment_statistics(self):
        """
        Test that valid segment statistics pass validation.
        
        Verifies:
        - All required fields are accepted
        - Types are validated correctly
        """
        stats = SegmentStatistics(
            segment="Monthly, High-Value Buyers",
            high_risk_count=150,
            medium_risk_count=200,
            med_high_ratio=0.35,
            med_high_monetary_sum=125000.50
        )
        
        assert stats.segment == "Monthly, High-Value Buyers"
        assert stats.high_risk_count == 150
        assert stats.med_high_ratio == 0.35
    
    def test_segment_statistics_with_zero_values(self):
        """
        Test that zero values are accepted.
        
        Verifies:
        - Zero counts are valid
        - Zero ratio is valid
        """
        stats = SegmentStatistics(
            segment="Seasonal Buyers",
            high_risk_count=0,
            medium_risk_count=0,
            med_high_ratio=0.0,
            med_high_monetary_sum=0.0
        )
        
        assert stats.high_risk_count == 0
        assert stats.med_high_ratio == 0.0
    
    def test_segment_statistics_missing_field(self):
        """
        Test that missing fields raise ValidationError.
        
        Verifies:
        - Missing required fields cause validation error
        """
        with pytest.raises(ValidationError):
            SegmentStatistics(
                segment="Monthly, High-Value Buyers",
                high_risk_count=150,
                # Missing medium_risk_count
                med_high_ratio=0.35,
                med_high_monetary_sum=125000.50
            )


class TestProcessDataResponse:
    """Test suite for ProcessDataResponse schema."""
    
    def test_valid_process_data_response(self):
        """
        Test that valid process data response passes validation.
        
        Verifies:
        - All required fields are accepted
        - Nested schemas are validated
        """
        response = ProcessDataResponse(
            status="success",
            message="Data processed successfully",
            data=[
                CustomerRecord(
                    customer_id=12345.0,
                    recency=30,
                    frequency=5,
                    monetary=1250.50,
                    median_purchase_days=15.0,
                    churn_ratio=2.0,
                    churn_label="High Risk",
                    monetary_log=7.13,
                    cluster_assignment=1,
                    segment="Monthly, High-Value Buyers"
                )
            ],
            total_customers=1,
            segment_statistics=[
                SegmentStatistics(
                    segment="Monthly, High-Value Buyers",
                    high_risk_count=1,
                    medium_risk_count=0,
                    med_high_ratio=1.0,
                    med_high_monetary_sum=1250.50
                )
            ]
        )
        
        assert response.status == "success"
        assert len(response.data) == 1
        assert response.total_customers == 1
        assert len(response.segment_statistics) == 1
    
    def test_process_data_response_with_empty_data(self):
        """
        Test that empty data list is accepted.
        
        Verifies:
        - Empty data list is valid
        - Empty segment_statistics is valid
        """
        response = ProcessDataResponse(
            status="success",
            message="Data processed successfully",
            data=[],
            total_customers=0,
            segment_statistics=[]
        )
        
        assert len(response.data) == 0
        assert response.total_customers == 0


class TestCustomerRecommendationResponse:
    """Test suite for CustomerRecommendationResponse schema."""
    
    def test_valid_customer_recommendation_response(self):
        """
        Test that valid recommendation response passes validation.
        
        Verifies:
        - Customer record is validated
        - Recommendation string is accepted
        """
        response = CustomerRecommendationResponse(
            customer=CustomerRecord(
                customer_id=12345.0,
                recency=30,
                frequency=5,
                monetary=1250.50,
                median_purchase_days=15.0,
                churn_ratio=2.0,
                churn_label="High Risk",
                monetary_log=7.13,
                cluster_assignment=1,
                segment="Monthly, High-Value Buyers"
            ),
            recommendation="This is a test recommendation."
        )
        
        assert response.customer.customer_id == 12345.0
        assert response.recommendation == "This is a test recommendation."
    
    def test_customer_recommendation_response_with_empty_recommendation(self):
        """
        Test that empty recommendation string is accepted.
        
        Verifies:
        - Empty string is valid (though not ideal)
        """
        response = CustomerRecommendationResponse(
            customer=CustomerRecord(
                customer_id=12345.0,
                recency=30,
                frequency=5,
                monetary=1250.50,
                median_purchase_days=15.0,
                churn_ratio=2.0,
                churn_label="High Risk",
                monetary_log=7.13,
                cluster_assignment=1,
                segment="Monthly, High-Value Buyers"
            ),
            recommendation=""
        )
        
        assert response.recommendation == ""
    
    def test_customer_recommendation_response_missing_customer(self):
        """
        Test that missing customer raises ValidationError.
        
        Verifies:
        - Missing required customer field causes error
        """
        with pytest.raises(ValidationError):
            CustomerRecommendationResponse(
                # Missing customer
                recommendation="Test recommendation"
            )
