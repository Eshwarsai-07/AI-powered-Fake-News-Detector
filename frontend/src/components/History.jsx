/**
 * History Component
 * Displays recent prediction history from the backend.
 */

import { useState, useEffect } from 'react';
import { getHistory } from '../api';

function History() {
  const [predictions, setPredictions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getHistory();
      setPredictions(data.predictions || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="history-section">
        <h2>Recent Analysis History</h2>
        <div className="history-loading">
          <span className="spinner"></span>
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-section">
        <h2>Recent Analysis History</h2>
        <div className="history-error">
          <p>⚠️ {error}</p>
          <button className="btn btn-secondary" onClick={fetchHistory}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (predictions.length === 0) {
    return (
      <div className="history-section">
        <h2>Recent Analysis History</h2>
        <div className="history-empty">
          <p>No predictions yet. Start analyzing news articles to see history here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-section">
      <div className="history-header">
        <h2>Recent Analysis History</h2>
        <button className="btn btn-secondary btn-sm" onClick={fetchHistory}>
          🔄 Refresh
        </button>
      </div>

      <div className="history-list">
        {predictions.map((pred, index) => (
          <div key={index} className="history-item">
            <div className="history-item-header">
              <span className={`history-badge ${pred.prediction === 'Fake' ? 'badge-fake' : 'badge-real'}`}>
                {pred.prediction}
              </span>
              <span className="history-confidence">
                {Math.round(pred.confidence * 100)}%
              </span>
              <span className="history-date">
                {formatDate(pred.created_at)}
              </span>
            </div>
            <p className="history-text">
              {truncateText(pred.text)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default History;
