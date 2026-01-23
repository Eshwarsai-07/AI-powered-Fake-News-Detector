"""
MongoDB database connection and operations.
Uses Motor (async MongoDB driver) for FastAPI integration.
"""

import logging
from typing import List, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from .config import MONGODB_URI, DATABASE_NAME


logger = logging.getLogger(__name__)


class MongoDB:
    """
    MongoDB connection manager using Motor async driver.
    Handles connection lifecycle and provides access to collections.
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.predictions: Optional[AsyncIOMotorCollection] = None
        self._is_connected: bool = False
    
    async def connect(self) -> bool:
        """
        Connect to MongoDB (local or Atlas).
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MongoDB: {DATABASE_NAME}")
            
            # Detect if using MongoDB Atlas or local MongoDB
            is_atlas = "mongodb+srv://" in MONGODB_URI or "mongodb.net" in MONGODB_URI
            
            # Create async MongoDB client with appropriate configuration
            if is_atlas:
                # MongoDB Atlas requires TLS
                self.client = AsyncIOMotorClient(
                    MONGODB_URI,
                    tls=True,
                    tlsAllowInvalidCertificates=True,
                    serverSelectionTimeoutMS=5000
                )
            else:
                # Local MongoDB (explicitly disable TLS)
                self.client = AsyncIOMotorClient(
                    MONGODB_URI,
                    tls=False,  # Explicitly disable TLS
                    serverSelectionTimeoutMS=5000
                )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database and collection references
            self.db = self.client[DATABASE_NAME]
            self.predictions = self.db["predictions"]
            
            # Create index on created_at for faster sorting
            await self.predictions.create_index([("created_at", -1)])
            
            self._is_connected = True
            logger.info("MongoDB connected successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self._is_connected = False
            return False
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._is_connected = False
            logger.info("MongoDB disconnected")
    
    @property
    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        return self._is_connected
    
    async def save_prediction(
        self,
        text: str,
        prediction: str,
        confidence: float,
        model_version: str
    ) -> Optional[str]:
        """
        Save a prediction to the database.
        
        Args:
            text: The news article text
            prediction: "Fake" or "Real"
            confidence: Confidence score (0.0 to 1.0)
            model_version: Model version identifier
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self._is_connected:
            logger.warning("Cannot save prediction: MongoDB not connected")
            return None
        
        try:
            document = {
                "text": text,
                "prediction": prediction,
                "confidence": confidence,
                "model_version": model_version,
                "created_at": datetime.utcnow()
            }
            
            result = await self.predictions.insert_one(document)
            logger.info(f"Saved prediction: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to save prediction: {str(e)}")
            return None
    
    async def get_recent_predictions(self, limit: int = 10) -> List[dict]:
        """
        Retrieve recent predictions from the database.
        
        Args:
            limit: Maximum number of predictions to return
            
        Returns:
            List of prediction documents (newest first)
        """
        if not self._is_connected:
            logger.warning("Cannot fetch predictions: MongoDB not connected")
            return []
        
        try:
            cursor = self.predictions.find(
                {},
                {
                    "_id": 0,  # Exclude MongoDB _id from response
                    "text": 1,
                    "prediction": 1,
                    "confidence": 1,
                    "model_version": 1,
                    "created_at": 1
                }
            ).sort("created_at", -1).limit(limit)
            
            predictions = await cursor.to_list(length=limit)
            
            # Convert datetime to ISO string for JSON serialization
            for pred in predictions:
                if "created_at" in pred:
                    pred["created_at"] = pred["created_at"].isoformat()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to fetch predictions: {str(e)}")
            return []


# Global MongoDB instance
mongodb = MongoDB()
