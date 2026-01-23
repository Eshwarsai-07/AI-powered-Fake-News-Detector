"""
Configuration settings for the Fake News Detector API.
Centralizes all configuration values including model paths and app settings.
"""

import os
from pathlib import Path


# Base directory (backend folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# Model configuration
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(BASE_DIR.parent / "model_training" / "saved_model" / "fake-news-bert")
)

# API configuration
API_TITLE = "Fake News Detector API"
API_DESCRIPTION = """
A production-ready API for detecting fake news using a fine-tuned BERT model.

## Features
- **Text Analysis**: Submit news text and receive Fake/Real prediction
- **Confidence Scoring**: Get confidence percentage for predictions
"""
API_VERSION = "1.0.0"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Model labels
LABEL_MAP = {
    0: "Fake",
    1: "Real"
}

# Optional Security
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", None)

# MongoDB configuration
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"  # Default for local development
)
DATABASE_NAME = os.getenv("DATABASE_NAME", "fake_news_db")

# Model version for tracking predictions
MODEL_VERSION = os.getenv("MODEL_VERSION", "fake-news-bert-v1")
