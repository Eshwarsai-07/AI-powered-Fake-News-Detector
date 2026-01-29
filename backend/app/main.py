"""
FastAPI application entry point.
Defines API endpoints and application lifecycle.
"""

import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from contextlib import asynccontextmanager
from collections import defaultdict
import time

from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS, MODEL_VERSION, API_KEY_NAME, API_KEY
from .schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from .model import classifier
from app.database import verify_db_connection
# Trigger CI/CD Pipeline verification
from app.model import analyze_news, load_model
from prometheus_fastapi_instrumentator import Instrumentator



# Simple in-memory rate limiter
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

def is_rate_limited(client_ip: str) -> bool:
    """Check if client IP is rate limited."""
    now = time.time()
    # Clean old requests
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW]
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return True
    # Add current request
    rate_limit_store[client_ip].append(now)
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Loads the model at startup and handles cleanup at shutdown.
    """
    # Startup: Load the model
    logger.info("Starting up - Loading ML model...")
    success = classifier.load()
    if not success:
        logger.warning("Model failed to load. API will return errors for predictions.")
    
    # Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    db_success = await mongodb.connect()
    if not db_success:
        logger.warning("MongoDB connection failed. History features will be unavailable.")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    logger.info("Shutting down...")
    await mongodb.disconnect()

# Security Scheme
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def version_middleware(request: Request, call_next):
    """Add version header to response."""
    response = await call_next(request)
    response.headers["X-API-Version"] = API_VERSION
    return response

async def latency_middleware(request: Request, call_next):
    """Log request latency."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Add scalar header for monitoring
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key if configured."""
    if API_KEY and api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials"
        )
    return api_key


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)] if API_KEY else None
)

app.middleware("http")(latency_middleware)
app.middleware("http")(version_middleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)



@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "model_loaded": classifier.is_loaded
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_text(request: AnalyzeRequest, req: Request):
    """
    Analyze news text for fake news detection.
    
    Takes a news article text and returns:
    - **prediction**: "Fake" or "Real"
    - **confidence**: Probability score (0.0 to 1.0)
    
    The model uses a fine-tuned BERT classifier trained on fake news datasets.
    """
    # Rate limiting
    client_ip = req.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    # Check if model is loaded
    if not classifier.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please try again later."
        )
    
    try:
        # Make prediction
        prediction, confidence = classifier.predict(request.text)
        
        # Save to MongoDB (non-blocking, failures are logged but don't affect response)
        if mongodb.is_connected:
            await mongodb.save_prediction(
                text=request.text,
                prediction=prediction,
                confidence=confidence,
                model_version=MODEL_VERSION
            )
        
        return AnalyzeResponse(
            prediction=prediction,
            confidence=confidence
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis. Please try again."
        )


@app.get("/history", tags=["History"])
async def get_history(limit: int = 10):
    """
    Retrieve recent prediction history.
    
    Returns the latest predictions sorted by newest first.
    
    Args:
        limit: Maximum number of predictions to return (default: 10, max: 50)
    """
    # Validate limit
    if limit < 1:
        limit = 10
    elif limit > 50:
        limit = 50
    
    # Check if MongoDB is connected
    if not mongodb.is_connected:
        raise HTTPException(
            status_code=503,
            detail="History service is unavailable. Database not connected."
        )
    
    try:
        predictions = await mongodb.get_recent_predictions(limit=limit)
        return {
            "count": len(predictions),
            "predictions": predictions
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve prediction history."
        )
