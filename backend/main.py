from fastapi import FastAPI, UploadFile, File, HTTPException
from schemas import ProcessDataResponse, CustomerRecord, SegmentStatistics, CustomerRecommendationResponse
from utils.pipelines import ingest_data, transform_data, add_features, _calculate_segment_statistics
from typing import List, Dict, Optional
import tempfile
import os
import pandas as pd
import math

# In-memory storage for processed customer data
# Key: customer_id (float), Value: CustomerRecord dict
_customer_cache: Dict[float, dict] = {}

# Create FastAPI app instance
app = FastAPI(
    title="Gifts Exercise API",
    description="API for gifts exercise data processing",
    version="1.0.0"
)


@app.post("/api/process-data", response_model=ProcessDataResponse)
async def process_data(file: UploadFile = File(...)):
    """
    Process parquet file and return customer segmentation data.
    
    Accepts a parquet file upload, processes it through the data pipeline,
    and returns customer-level data with RFM metrics and segmentation
    in a format suitable for React frontend visualization.
    
    Args:
        file: Uploaded parquet file containing transaction data
    
    Returns:
        ProcessDataResponse containing:
        - status: Processing status
        - message: Status message
        - data: List of customer records with RFM metrics and segments
        - total_customers: Total number of customers processed
    """
    # Validate file type
    if not file.filename.endswith('.parquet'):
        raise HTTPException(
            status_code=400,
            detail="File must be a parquet file (.parquet)"
        )
    
    # Create temporary file to save uploaded parquet
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        # Process the data through pipeline
        # Step 1: Ingest data
        raw_df = ingest_data(temp_file)
        
        # Step 2: Transform data
        full_df = transform_data(raw_df)
        
        # Step 3: Add features and create aggregations
        _, _, customer_df = add_features(full_df)
        
        # Select only the columns we need for the response
        # Ensure column order matches the schema
        columns_to_return = [
            'customer_id',
            'recency',
            'frequency',
            'monetary',
            'median_purchase_days',
            'churn_ratio',
            'churn_label',
            'monetary_log',
            'cluster_assignment',
            'segment'
        ]
        customer_df = customer_df[columns_to_return]

        # Sort by churn_ratio (highest to lowest), then by monetary (highest to lowest)
        customer_df = customer_df.sort_values(
            by=['churn_ratio', 'monetary'],
            ascending=[False, False],
            na_position='last'  # Put NaN values at the end
        )
        
        # Convert to records format (list of dicts) - easy for React to work with
        customer_records = customer_df.to_dict(orient='records')
        
        # Replace NaN/NaT/inf values with None for proper JSON serialization
        for record in customer_records:
            for key, value in record.items():
                # Check if value is NaN (handles both pandas and numpy NaN)
                if pd.isna(value):
                    record[key] = None
                # Check if value is infinity (can occur in churn_ratio if division by zero)
                elif isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
                    record[key] = None
        
        # Store customer data in cache for later retrieval by recommendation endpoint
        for record in customer_records:
            _customer_cache[record['customer_id']] = record
        
        # Convert to Pydantic models for validation
        customer_data = [CustomerRecord(**record) for record in customer_records]
        
        # Calculate aggregate statistics by segment
        segment_stats = _calculate_segment_statistics(customer_df)
        
        return ProcessDataResponse(
            status="success",
            message="Data processed successfully",
            data=customer_data,
            total_customers=len(customer_data),
            segment_statistics=segment_stats
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


@app.get("/api/customer/{customer_id}/recommendation", response_model=CustomerRecommendationResponse)
async def get_customer_recommendation(customer_id: float):
    """
    Get individual customer data and recommendation.
    
    Retrieves a single customer's data and generates a text recommendation
    based on their segment and churn risk.
    
    Args:
        customer_id: The customer ID to retrieve
    
    Returns:
        CustomerRecommendationResponse containing customer data and recommendation
    """
    # Check if customer exists in cache
    if customer_id not in _customer_cache:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found. Please process data first using /api/process-data endpoint."
        )
    
    # Get customer record from cache
    customer_record_dict = _customer_cache[customer_id]
    customer_record = CustomerRecord(**customer_record_dict)
    
    # Generate recommendation based on segment and churn risk
    recommendation = _generate_recommendation(customer_record)
    
    return CustomerRecommendationResponse(
        customer=customer_record,
        recommendation=recommendation
    )


def _generate_recommendation(customer: CustomerRecord) -> str:
    """
    Generate recommendation text based on customer segment and churn risk.
    
    Args:
        customer: CustomerRecord with all customer data
    
    Returns:
        Text recommendation string
    """
    segment = customer.segment
    churn_label = customer.churn_label
    
    # TODO: Implement your recommendation logic here
    # This is a placeholder structure - replace with your actual conditions and outputs
    
    if segment == "Monthly, High-Value Buyers":
        if churn_label == "High Risk":
            return "Your recommendation text for High Risk Monthly, High-Value Buyers"
        elif churn_label == "Medium Risk":
            return "Your recommendation text for Medium Risk Monthly, High-Value Buyers"
        else:  # Low Risk
            return "Your recommendation text for Low Risk Monthly, High-Value Buyers"
    
    elif segment == "Seasonal Buyers":
        if churn_label == "High Risk":
            return "Your recommendation text for High Risk Seasonal Buyers"
        elif churn_label == "Medium Risk":
            return "Your recommendation text for Medium Risk Seasonal Buyers"
        else:  # Low Risk
            return "Your recommendation text for Low Risk Seasonal Buyers"
    
    else:  # Experimental / Hesitant, Lower-Value Buyers
        if churn_label == "High Risk":
            return "Your recommendation text for High Risk Experimental/Hesitant Buyers"
        elif churn_label == "Medium Risk":
            return "Your recommendation text for Medium Risk Experimental/Hesitant Buyers"
        else:  # Low Risk
            return "Your recommendation text for Low Risk Experimental/Hesitant Buyers"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
