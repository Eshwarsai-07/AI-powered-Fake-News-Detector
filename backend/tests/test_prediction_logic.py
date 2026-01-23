"""
Test suite for the improved prediction logic.
Validates confidence-aware decision making and edge cases.
"""

import pytest
from backend.app.model import FakeNewsClassifier, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


# Sample test texts
LONG_REAL_ARTICLE = """
Scientists at MIT have developed a revolutionary solar panel technology 
that can generate electricity from thermal radiation at night. The research, 
published in Nature Energy, shows a 20% efficiency improvement over 
traditional panels. The team spent 5 years developing the prototype 
and testing it under various conditions. The breakthrough could transform 
renewable energy infrastructure worldwide.
"""

LONG_FAKE_ARTICLE = """
BREAKING: Aliens landed in New York City yesterday and the government 
is covering it up. Multiple witnesses saw UFOs hovering over Times Square. 
The mainstream media refuses to report this because they are controlled 
by the deep state. Share this before it gets deleted! Wake up sheeple!
This is the truth they don't want you to know about.
"""

AMBIGUOUS_HEADLINE = "Shocking: Government Hides Truth About Vaccines"

SHORT_GENERIC = "The economy is doing well."

VERY_SHORT = "News today"


class TestPredictionLogic:
    """Test suite for confidence-aware prediction logic."""
    
    @pytest.fixture
    def classifier(self):
        """Create and load classifier instance."""
        clf = FakeNewsClassifier()
        clf.load()
        return clf
    
    def test_input_validation_empty(self, classifier):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="non-empty"):
            classifier.predict_news_final("")
    
    def test_input_validation_too_short(self, classifier):
        """Test that very short input raises ValueError."""
        with pytest.raises(ValueError, match="too short"):
            classifier.predict_news_final("Hi")
    
    def test_input_validation_whitespace(self, classifier):
        """Test that whitespace-only input raises ValueError."""
        with pytest.raises(ValueError, match="whitespace"):
            classifier.predict_news_final("   \n\t  ")
    
    def test_high_confidence_real_article(self, classifier):
        """Test that high-confidence real article returns 'Real'."""
        prediction, confidence = classifier.predict_news_final(LONG_REAL_ARTICLE)
        
        assert prediction in ["Real", "Uncertain"]
        assert 0.0 <= confidence <= 1.0
        
        # If confidence is high, should return Real
        if confidence >= CONFIDENCE_HIGH:
            assert prediction == "Real"
    
    def test_high_confidence_fake_article(self, classifier):
        """Test that high-confidence fake article returns 'Fake'."""
        prediction, confidence = classifier.predict_news_final(LONG_FAKE_ARTICLE)
        
        assert prediction in ["Fake", "Uncertain"]
        assert 0.0 <= confidence <= 1.0
        
        # If confidence is high, should return Fake
        if confidence >= CONFIDENCE_HIGH:
            assert prediction == "Fake"
    
    def test_ambiguous_headline_returns_uncertain(self, classifier):
        """Test that ambiguous headlines return 'Uncertain' or require high confidence."""
        prediction, confidence = classifier.predict_news_final(AMBIGUOUS_HEADLINE)
        
        # Headlines should either be Uncertain or have very high confidence (>0.95)
        if prediction != "Uncertain":
            assert confidence >= 0.95
    
    def test_low_confidence_returns_uncertain(self, classifier):
        """Test that low confidence predictions return 'Uncertain'."""
        prediction, confidence = classifier.predict_news_final(SHORT_GENERIC)
        
        # Low confidence should always return Uncertain
        if confidence < CONFIDENCE_MEDIUM:
            assert prediction == "Uncertain"
    
    def test_prediction_format(self, classifier):
        """Test that prediction returns correct format."""
        prediction, confidence = classifier.predict_news_final(LONG_REAL_ARTICLE)
        
        # Check types
        assert isinstance(prediction, str)
        assert isinstance(confidence, float)
        
        # Check values
        assert prediction in ["Real", "Fake", "Uncertain"]
        assert 0.0 <= confidence <= 1.0
        
        # Check confidence precision
        assert len(str(confidence).split('.')[-1]) <= 4  # Max 4 decimal places
    
    def test_metadata_function(self, classifier):
        """Test predict_with_metadata returns correct structure."""
        result = classifier.predict_with_metadata(LONG_REAL_ARTICLE)
        
        # Check structure
        assert "prediction" in result
        assert "confidence" in result
        assert "metadata" in result
        
        # Check metadata fields
        metadata = result["metadata"]
        assert "is_headline_only" in metadata
        assert "text_length" in metadata
        assert "word_count" in metadata
        assert "confidence_category" in metadata
        
        # Check types
        assert isinstance(metadata["is_headline_only"], bool)
        assert isinstance(metadata["text_length"], int)
        assert isinstance(metadata["word_count"], int)
        assert metadata["confidence_category"] in ["high", "medium", "low"]
    
    def test_headline_detection(self, classifier):
        """Test headline detection logic."""
        # Short headline should be detected
        result = classifier.predict_with_metadata(AMBIGUOUS_HEADLINE)
        assert result["metadata"]["is_headline_only"] is True
        
        # Long article should not be detected as headline
        result = classifier.predict_with_metadata(LONG_REAL_ARTICLE)
        assert result["metadata"]["is_headline_only"] is False
    
    def test_backward_compatibility(self, classifier):
        """Test that legacy predict() method still works."""
        prediction, confidence = classifier.predict(LONG_REAL_ARTICLE)
        
        assert prediction in ["Real", "Fake", "Uncertain"]
        assert 0.0 <= confidence <= 1.0


# Manual test examples (run these manually for verification)
def manual_test_examples():
    """
    Manual test cases to verify prediction logic.
    Run this to see actual predictions on various inputs.
    """
    classifier = FakeNewsClassifier()
    classifier.load()
    
    test_cases = [
        ("Long Real Article", LONG_REAL_ARTICLE),
        ("Long Fake Article", LONG_FAKE_ARTICLE),
        ("Ambiguous Headline", AMBIGUOUS_HEADLINE),
        ("Short Generic", SHORT_GENERIC),
        ("Very Short", VERY_SHORT),
    ]
    
    print("\n" + "="*80)
    print("MANUAL TEST RESULTS")
    print("="*80 + "\n")
    
    for name, text in test_cases:
        try:
            prediction, confidence = classifier.predict_news_final(text)
            result = classifier.predict_with_metadata(text)
            
            print(f"Test: {name}")
            print(f"Text: {text[:100]}...")
            print(f"Prediction: {prediction}")
            print(f"Confidence: {confidence:.4f}")
            print(f"Is Headline: {result['metadata']['is_headline_only']}")
            print(f"Confidence Category: {result['metadata']['confidence_category']}")
            print("-" * 80 + "\n")
            
        except Exception as e:
            print(f"Test: {name}")
            print(f"ERROR: {str(e)}")
            print("-" * 80 + "\n")


if __name__ == "__main__":
    # Run manual tests
    manual_test_examples()
