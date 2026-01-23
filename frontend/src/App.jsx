/**
 * Main App component.
 * Orchestrates the fake news detection UI and handles state.
 */

import { useState } from 'react';
import { MIN_TEXT_LENGTH } from "./constants";
import TextInput from "./components/TextInput";
import ResultCard from "./components/ResultCard";
import History from "./components/History";
import { analyzeNews } from "./api";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    // Validate input
    if (!text.trim() || text.trim().length < MIN_TEXT_LENGTH) {
      setError(
        `Please enter at least ${MIN_TEXT_LENGTH} characters of text to analyze.`,
      );
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeNews(text);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🔍</span>
            <h1>Fake News Detector</h1>
          </div>
          <p className="tagline">AI-powered credibility analysis using BERT</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <TextInput
            value={text}
            onChange={setText}
            onAnalyze={handleAnalyze}
            onClear={handleClear}
            isLoading={isLoading}
          />

          {error && (
            <div className="error-card">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
            </div>
          )}

          {result && <ResultCard result={result} />}

          <section className="info-section">
            <h2>How it works</h2>
            <div className="info-grid">
              <div className="info-card">
                <span className="info-icon">📝</span>
                <h3>Paste Text</h3>
                <p>Enter the news article or headline you want to verify</p>
              </div>
              <div className="info-card">
                <span className="info-icon">🤖</span>
                <h3>AI Analysis</h3>
                <p>Our BERT model analyzes the text patterns and language</p>
              </div>
              <div className="info-card">
                <span className="info-icon">✅</span>
                <h3>Get Results</h3>
                <p>Receive a credibility score with confidence percentage</p>
              </div>
            </div>
          </section>

          <History />
        </div>
      </main>

      <footer className="footer">
        <p>Built with FastAPI & React • BERT-based NLP Model</p>
      </footer>
    </div>
  );
}

export default App;
