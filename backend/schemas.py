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


class ProcessDataResponse(BaseModel):
    """Response schema for data processing endpoint."""
    status: str
    message: str
    data: List[CustomerRecord]
    total_customers: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Data processed successfully",
                "total_customers": 4316,
                "data": []
            }
        }
