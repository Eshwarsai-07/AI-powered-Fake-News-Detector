/**
 * TextInput Component
 * Provides a textarea for news input and action buttons.
 */

import { MIN_TEXT_LENGTH } from "../constants";

function TextInput({ value, onChange, onAnalyze, onClear, isLoading }) {
  const handleKeyDown = (e) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onAnalyze();
    }
  };

  return (
    <div className="input-section">
      <label htmlFor="news-input" className="input-label">
        Paste your news article or headline below
      </label>
      <textarea
        id="news-input"
        className="text-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Enter news text here... (minimum 10 characters)

Example: 'Scientists at MIT have developed a revolutionary new solar panel technology that can generate electricity even at night using thermal radiation.'"
        rows={8}
        disabled={isLoading}
      />
      <div className="input-footer">
        <span className="char-count">{value.length} characters</span>
        <div className="button-group">
          <button
            className="btn btn-secondary"
            onClick={onClear}
            disabled={isLoading || !value}
          >
            Clear
          </button>
          <button
            className="btn btn-primary"
            onClick={onAnalyze}
            disabled={isLoading || value.trim().length < MIN_TEXT_LENGTH}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                <span>🔍</span>
                Analyze
              </>
            )}
          </button>
        </div>
      </div>
      <p className="input-hint">
        💡 Tip: Press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> to analyze
      </p>
    </div>
  );
}

export default TextInput;
