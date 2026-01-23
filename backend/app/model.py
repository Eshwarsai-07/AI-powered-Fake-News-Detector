"""
Production-grade prediction function with confidence-aware decision logic.

This module provides an improved prediction interface that handles
ambiguous inputs by introducing an "UNCERTAIN" category for low-confidence
predictions, reducing false positives without retraining the model.
"""

import logging
from typing import Tuple, Dict, Any
import re

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .config import MODEL_PATH, LABEL_MAP
from .utils import clean_text, truncate_text


logger = logging.getLogger(__name__)


# Confidence thresholds for decision logic
CONFIDENCE_HIGH = 0.90      # Trust model output completely
CONFIDENCE_MEDIUM = 0.60    # Uncertain zone begins
MINIMUM_TEXT_LENGTH = 10    # Minimum characters after cleaning


class FakeNewsClassifier:
    """
    Wrapper class for the fake news detection BERT model.
    
    Loads the model and tokenizer once at startup and provides
    a production-ready prediction interface with confidence-aware logic.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.model: AutoModelForSequenceClassification = None
            self.tokenizer: AutoTokenizer = None
            self.device: str = "cpu"  # Force CPU for free-tier compatibility
            self._is_loaded: bool = False
            self._initialized = True
            
    def _warmup(self):
        """Run a dummy prediction to initialize lazy layers."""
        try:
            logger.info("Warming up model...")
            dummy_text = "This is a warmup sentence to initialize the model."
            inputs = self.tokenizer(
                dummy_text, return_tensors="pt", truncation=True, max_length=64, padding=True
            )
            with torch.no_grad():
                self.model(**inputs)
            logger.info("Warmup complete.")
        except Exception as e:
            logger.warning(f"Warmup failed (non-critical): {e}")
    
    def load(self) -> bool:
        """
        Load the model and tokenizer from disk.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            logger.info(f"Loading model from: {MODEL_PATH}")
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            
            # Load model
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            
            # OPTIMIZATION: Dynamic Quantization for CPU
            # Reduces memory usage by ~40% and improves inference speed
            try:
                logger.info("Applying dynamic quantization...")
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
            except Exception as qe:
                logger.warning(f"Quantization failed, using full precision: {qe}")

            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            # OPTIMIZATION: Warmup
            self._warmup()
            
            self._is_loaded = True
            logger.info("Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self._is_loaded = False
            return False
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        return self._is_loaded
    
    def _validate_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate input text before prediction.
        
        Args:
            text: Raw input text
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not isinstance(text, str):
            return False, "Input must be a non-empty string"
        
        # Check if text is too short (likely just a headline or fragment)
        if len(text.strip()) < MINIMUM_TEXT_LENGTH:
            return False, f"Text too short (minimum {MINIMUM_TEXT_LENGTH} characters)"
        
        # Check if text is only whitespace
        if not text.strip():
            return False, "Text contains only whitespace"
        
        return True, ""
    
    def _is_headline_only(self, text: str) -> bool:
        """
        Detect if input is likely just a headline (short, no punctuation).
        
        Headlines are often ambiguous and should be treated with caution.
        
        Args:
            text: Cleaned text
            
        Returns:
            True if likely a headline, False otherwise
        """
        # Count sentences (rough heuristic: periods, exclamation, question marks)
        sentence_endings = len(re.findall(r'[.!?]', text))
        word_count = len(text.split())
        
        # If very short and no sentence structure, likely a headline
        if word_count < 15 and sentence_endings == 0:
            return True
        
        # If only one sentence and very short, also likely a headline
        if word_count < 20 and sentence_endings <= 1:
            return True
        
        return False
    
    def predict_news_final(self, text: str) -> Tuple[str, float]:
        """
        Production-ready prediction function with confidence-aware logic.
        
        Decision Logic:
        1. Validate input (length, content)
        2. Detect headline-only inputs → apply stricter threshold
        3. Get model prediction with confidence
        4. Apply confidence-based decision:
           - confidence >= 0.90 → Trust model (REAL or FAKE)
           - 0.60 <= confidence < 0.90 → UNCERTAIN
           - confidence < 0.60 → UNCERTAIN
        
        This approach reduces false positives on ambiguous inputs
        without retraining the model.
        
        Args:
            text: News article text to classify
            
        Returns:
            Tuple of (prediction_label, confidence_score)
            - prediction_label: "Real", "Fake", or "Uncertain"
            - confidence_score: 0.0 to 1.0
            
        Raises:
            RuntimeError: If model is not loaded
            ValueError: If input validation fails
        """
        if not self._is_loaded:
            raise RuntimeError("Model is not loaded. Call load() first.")
        
        # Step 1: Validate input
        is_valid, error_msg = self._validate_input(text)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Step 2: Preprocess text
        cleaned_text = clean_text(text)
        cleaned_text = truncate_text(cleaned_text)
        
        if not cleaned_text or len(cleaned_text) < MINIMUM_TEXT_LENGTH:
            raise ValueError("Text is empty or too short after preprocessing")
        
        # Step 3: Check if input is headline-only (ambiguous)
        is_headline = self._is_headline_only(cleaned_text)
        
        # Step 4: Tokenize
        inputs = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Step 5: Model inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
            # Apply softmax to get probabilities
            probabilities = torch.softmax(logits, dim=-1)
            
            # Get prediction and confidence
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # Step 6: Map to label
        raw_prediction = LABEL_MAP.get(predicted_class, "Unknown")
        
        # Step 7: Apply confidence-aware decision logic
        final_prediction, final_confidence = self._apply_confidence_logic(
            raw_prediction, 
            confidence, 
            is_headline
        )
        
        # Log prediction for monitoring
        logger.info(
            f"Prediction: {final_prediction} (confidence: {final_confidence:.4f}, "
            f"raw: {raw_prediction}, is_headline: {is_headline})"
        )
        
        return final_prediction, round(final_confidence, 4)
    
    def _apply_confidence_logic(
        self, 
        prediction: str, 
        confidence: float, 
        is_headline: bool
    ) -> Tuple[str, float]:
        """
        Apply confidence-based decision rules.
        
        Args:
            prediction: Raw model prediction ("Real" or "Fake")
            confidence: Model confidence score (0.0 to 1.0)
            is_headline: Whether input appears to be headline-only
            
        Returns:
            Tuple of (final_prediction, final_confidence)
        """
        # For headline-only inputs, require higher confidence
        threshold_high = 0.95 if is_headline else CONFIDENCE_HIGH
        
        # High confidence: Trust the model
        if confidence >= threshold_high:
            return prediction, confidence
        
        # Medium confidence: Uncertain
        elif confidence >= CONFIDENCE_MEDIUM:
            return "Uncertain", confidence
        
        # Low confidence: Uncertain
        else:
            return "Uncertain", confidence
    
    def predict_with_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extended prediction function that returns additional metadata.
        
        Useful for debugging, monitoring, and explainability.
        
        Args:
            text: News article text
            
        Returns:
            Dictionary with prediction, confidence, and metadata
        """
        if not self._is_loaded:
            raise RuntimeError("Model is not loaded. Call load() first.")
        
        # Validate and preprocess
        is_valid, error_msg = self._validate_input(text)
        if not is_valid:
            raise ValueError(error_msg)
        
        cleaned_text = clean_text(text)
        is_headline = self._is_headline_only(cleaned_text)
        
        # Get prediction
        prediction, confidence = self.predict_news_final(text)
        
        # Return with metadata
        return {
            "prediction": prediction,
            "confidence": confidence,
            "metadata": {
                "is_headline_only": is_headline,
                "text_length": len(cleaned_text),
                "word_count": len(cleaned_text.split()),
                "confidence_category": self._get_confidence_category(confidence)
            }
        }
    
    def _get_confidence_category(self, confidence: float) -> str:
        """Categorize confidence level for reporting."""
        if confidence >= CONFIDENCE_HIGH:
            return "high"
        elif confidence >= CONFIDENCE_MEDIUM:
            return "medium"
        else:
            return "low"
    
    # Legacy method for backward compatibility
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Legacy prediction method (calls predict_news_final).
        
        Maintained for backward compatibility with existing API.
        """
        return self.predict_news_final(text)


# Global classifier instance (initialized at startup)
classifier = FakeNewsClassifier()
