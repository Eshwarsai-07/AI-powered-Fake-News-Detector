"""
Pydantic schemas for request/response validation.
Ensures type safety and automatic documentation generation.
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request schema for the /analyze endpoint."""
    
    text: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="The news article text to analyze",
        json_schema_extra={
            "example": "Scientists discover new breakthrough in renewable energy technology."
        }
    )


class AnalyzeResponse(BaseModel):
    """Response schema for the /analyze endpoint."""
    
    prediction: str = Field(
        ...,
        description="The prediction result: 'Fake', 'Real', or 'Uncertain'",
        json_schema_extra={"example": "Real"}
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
        json_schema_extra={"example": 0.92}
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    
    status: str = Field(..., description="API health status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
