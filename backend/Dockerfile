# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for fastparquet and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements first for better Docker layer caching
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY main.py .
COPY schemas.py .
COPY utils/ ./utils/

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Run the application
# Use PORT environment variable (Railway/Render will set this)
# Default to 8000 if PORT is not set
CMD sh -c "python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
