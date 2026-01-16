"""
Test suite for recommendation generation function.

Tests include:
- Recommendation generation for all segments
- Null value handling
- Edge cases
"""

import pytest
from schemas import CustomerRecord


def _generate_recommendation(customer):
    """Import the function for testing."""
    from utils.recommendations import _generate_recommendation
    return _generate_recommendation(customer)


class TestGenerateRecommendation:
    """Test suite for _generate_recommendation function."""
    
    def test_recommendation_monthly_high_value_buyers(self):
        """
        Test recommendation generation for Monthly, High-Value Buyers segment.
        
        Verifies:
        - Recommendation is generated
        - Recommendation text is not empty
        - Contains relevant information
        """
        customer = CustomerRecord(
            customer_id=12345.0,
            recency=30,
            frequency=12,
            monetary=5000.0,
            median_purchase_days=30.0,
            churn_ratio=1.0,
            churn_label="Low Risk",
            monetary_log=8.52,
            cluster_assignment=1,
            segment="Monthly, High-Value Buyers"
        )
        
        recommendation = _generate_recommendation(customer)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert "12" in recommendation  # frequency
        assert "5000" in recommendation or "$5000" in recommendation  # monetary
    
    def test_recommendation_seasonal_buyers(self):
        """
        Test recommendation generation for Seasonal Buyers segment.
        
        Verifies:
        - Recommendation is generated for seasonal buyers
        - Contains relevant information
        """
        customer = CustomerRecord(
            customer_id=23456.0,
            recency=90,
            frequency=4,
            monetary=2000.0,
            median_purchase_days=90.0,
            churn_ratio=1.0,
            churn_label="Low Risk",
            monetary_log=7.60,
            cluster_assignment=0,
            segment="Seasonal Buyers"
        )
        
        recommendation = _generate_recommendation(customer)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert "90" in recommendation  # recency
        assert "4" in recommendation  # frequency
    
    def test_recommendation_experimental_buyers(self):
        """
        Test recommendation generation for Experimental/Hesitant Buyers segment.
        
        Verifies:
        - Recommendation is generated for experimental buyers
        - Contains relevant information
        """
        customer = CustomerRecord(
            customer_id=34567.0,
            recency=120,
            frequency=2,
            monetary=150.0,
            median_purchase_days=60.0,
            churn_ratio=2.0,
            churn_label="High Risk",
            monetary_log=5.01,
            cluster_assignment=2,
            segment="Experimental / Hesitant, Lower-Value Buyers"
        )
        
        recommendation = _generate_recommendation(customer)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert "2" in recommendation  # frequency
        assert "120" in recommendation  # recency
    
    def test_recommendation_with_null_churn_label(self):
        """
        Test recommendation generation when churn_label is None.
        
        Verifies:
        - Function handles null churn_label gracefully
        - Recommendation is still generated
        """
        customer = CustomerRecord(
            customer_id=45678.0,
            recency=0,
            frequency=1,
            monetary=100.0,
            median_purchase_days=0.0,
            churn_ratio=None,
            churn_label=None,
            monetary_log=4.61,
            cluster_assignment=2,
            segment="Experimental / Hesitant, Lower-Value Buyers"
        )
        
        # Should not crash even with null churn_label
        recommendation = _generate_recommendation(customer)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
    
    def test_recommendation_with_zero_values(self):
        """
        Test recommendation generation with zero recency, frequency, or monetary.
        
        Verifies:
        - Zero values don't break recommendation generation
        - Recommendation is still generated
        """
        customer = CustomerRecord(
            customer_id=56789.0,
            recency=0,
            frequency=1,
            monetary=0.0,
            median_purchase_days=0.0,
            churn_ratio=None,
            churn_label=None,
            monetary_log=0.0,
            cluster_assignment=2,
            segment="Experimental / Hesitant, Lower-Value Buyers"
        )
        
        recommendation = _generate_recommendation(customer)
        
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
    
    def test_recommendation_all_segments_covered(self):
        """
        Test that all three segments have recommendation logic.
        
        Verifies:
        - All segments return recommendations
        - No segment is missing
        """
        segments = [
            "Monthly, High-Value Buyers",
            "Seasonal Buyers",
            "Experimental / Hesitant, Lower-Value Buyers"
        ]
        
        for segment in segments:
            customer = CustomerRecord(
                customer_id=99999.0,
                recency=30,
                frequency=5,
                monetary=1000.0,
                median_purchase_days=30.0,
                churn_ratio=1.0,
                churn_label="Low Risk",
                monetary_log=6.91,
                cluster_assignment=0,
                segment=segment
            )
            
            recommendation = _generate_recommendation(customer)
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    def test_recommendation_contains_customer_data(self):
        """
        Test that recommendation text includes customer-specific data.
        
        Verifies:
        - Recommendation includes frequency
        - Recommendation includes monetary/annual value
        - Recommendation includes recency/days since last purchase
        """
        customer = CustomerRecord(
            customer_id=11111.0,
            recency=45,
            frequency=8,
            monetary=3000.0,
            median_purchase_days=30.0,
            churn_ratio=1.5,
            churn_label="Medium Risk",
            monetary_log=8.01,
            cluster_assignment=1,
            segment="Monthly, High-Value Buyers"
        )
        
        recommendation = _generate_recommendation(customer)
        
        # Check that customer data appears in recommendation
        assert "8" in recommendation  # frequency
        assert ("3000" in recommendation or "$3000" in recommendation)  # monetary
        assert "45" in recommendation  # recency
