from fastapi import FastAPI
from schemas import HelloWorldResponse

# Create FastAPI app instance
app = FastAPI(
    title="Gifts Exercise API",
    description="API for gifts exercise data processing",
    version="1.0.0"
)


@app.get("/", response_model=HelloWorldResponse)
async def hello_world():
    """
    Simple hello world endpoint.
    
    Returns a greeting message.
    """
    return HelloWorldResponse(message="hello world")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
