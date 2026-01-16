# Backend Test Suite

Comprehensive test suite for the gifts exercise backend using pytest.

## Test Coverage

### Test Files

- **test_endpoints.py**: Tests for FastAPI endpoints
  - Input validation (file types, parameters)
  - Output validation (response schemas)
  - Null and NaN value handling
  - Timeout scenarios
  - Error handling

- **test_pipelines.py**: Tests for data pipeline functions
  - Data ingestion
  - Data transformation
  - Feature engineering
  - Null and NaN handling
  - Edge cases

- **test_recommendations.py**: Tests for recommendation generation
  - Recommendation generation for all segments
  - Null value handling
  - Edge cases

- **test_schemas.py**: Tests for Pydantic schemas
  - Schema validation
  - Type checking
  - Optional field handling
  - Edge cases

## Running Tests

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test File

```bash
pytest tests/test_endpoints.py
pytest tests/test_pipelines.py
pytest tests/test_recommendations.py
pytest tests/test_schemas.py
```

### Run Specific Test Class

```bash
pytest tests/test_endpoints.py::TestProcessDataEndpoint
```

### Run Specific Test Function

```bash
pytest tests/test_endpoints.py::TestProcessDataEndpoint::test_valid_parquet_file_upload
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

### Run Only Fast Tests (Exclude Slow Tests)

```bash
pytest -m "not slow"
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `client`: FastAPI test client
- `sample_transaction_data`: Sample transaction DataFrame
- `sample_transaction_data_with_nulls`: DataFrame with null values
- `sample_transaction_data_with_negatives`: DataFrame with negative values (refunds)
- `sample_parquet_file`: Temporary parquet file with sample data
- `sample_parquet_file_with_nulls`: Parquet file with null values
- `sample_customer_record`: Sample customer record dictionary
- `sample_customer_record_with_nulls`: Customer record with null values
- `clear_cache`: Clears customer cache before/after tests

## Test Requirements

All test dependencies are included in `requirements.txt`:

- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `httpx`: HTTP client for testing (already in requirements)

## Notes

- Tests use temporary files and directories that are automatically cleaned up
- The customer cache is cleared before and after each test that uses it
- Some tests may require the actual data file to be present for full integration testing
