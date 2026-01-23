/**
 * API client for communicating with the FastAPI backend.
 * Centralizes all API calls and error handling.
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for model inference
});

/**
 * Analyze news text for fake news detection.
 * @param {string} text - The news article text to analyze
 * @returns {Promise<{prediction: string, confidence: number}>}
 */
export const analyzeNews = async (text) => {
  try {
    const response = await api.post('/analyze', { text });
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Analysis failed');
    } else if (error.request) {
      // No response received
      throw new Error('Unable to connect to server. Please try again.');
    } else {
      // Request setup error
      throw new Error('An unexpected error occurred');
    }
  }
};

/**
 * Check API health status.
 * @returns {Promise<{status: string, model_loaded: boolean}>}
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Health check failed');
  }
};

/**
 * Get recent prediction history.
 * @param {number} limit - Maximum number of predictions to retrieve (default: 10)
 * @returns {Promise<{count: number, predictions: Array}>}
 */
export const getHistory = async (limit = 10) => {
  try {
    const response = await api.get('/history', { params: { limit } });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to fetch history');
    } else if (error.request) {
      throw new Error('Unable to connect to server');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
};

export default api;
