"""
Utility functions for text preprocessing.
Cleans and normalizes input text before model inference.
"""

import re
import html


def clean_text(text: str) -> str:
    """
    Clean and preprocess input text for model inference.
    
    Performs the following operations:
    1. Decode HTML entities
    2. Remove HTML tags
    3. Remove URLs
    4. Remove extra whitespace
    5. Strip leading/trailing whitespace
    
    Args:
        text: Raw input text from user
        
    Returns:
        Cleaned text ready for tokenization
    """
    # Decode HTML entities (e.g., &amp; -> &)
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 512) -> str:
    """
    Truncate text to a maximum word count.
    
    BERT models typically have a 512 token limit, so we pre-truncate
    to avoid processing unnecessarily long texts.
    
    Args:
        text: Input text
        max_length: Maximum number of words to keep
        
    Returns:
        Truncated text
    """
    words = text.split()
    if len(words) > max_length:
        words = words[:max_length]
    return ' '.join(words)
