from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CustomerRecord(BaseModel):
    """Schema for a single customer record."""
    customer_id: float
    recency: int
    frequency: int
    monetary: float
    median_purchase_days: float
    churn_ratio: Optional[float]  # Can be None or inf in edge cases
    churn_label: Optional[str]  # "Low Risk", "Medium Risk", or "High Risk"
    monetary_log: float
    cluster_assignment: int
    segment: str

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class SegmentStatistics(BaseModel):
    """Schema for segment-level churn risk statistics."""
    segment: str
    high_risk_count: int
    medium_risk_count: int
    med_high_ratio: float  # Ratio of (Medium + High Risk) to total customers
    med_high_monetary_sum: float  # Total monetary value of Medium + High Risk customers

    class Config:
        json_schema_extra = {
            "example": {
                "segment": "Monthly, High-Value Buyers",
                "high_risk_count": 150,
                "medium_risk_count": 200,
                "med_high_ratio": 0.35,
                "med_high_monetary_sum": 125000.50
            }
        }


class ProcessDataResponse(BaseModel):
    """Response schema for data processing endpoint."""
    status: str
    message: str
    data: List[CustomerRecord]
    total_customers: int
    segment_statistics: List[SegmentStatistics]  # Aggregate statistics by segment

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Data processed successfully",
                "total_customers": 4316,
                "data": [],
                "segment_statistics": []
            }
        }


class CustomerRecommendationResponse(BaseModel):
    """Response schema for individual customer recommendation endpoint."""
    customer: CustomerRecord  # All customer data
    recommendation: str  # Text recommendation based on segment

    class Config:
        json_schema_extra = {
            "example": {
                "customer": {
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
                },
                "recommendation": "Based on your segment and churn risk, we recommend..."
            }
        }
