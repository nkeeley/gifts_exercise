from pydantic import BaseModel


class HelloWorldResponse(BaseModel):
    """Response schema for hello world endpoint."""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "hello world"
            }
        }
