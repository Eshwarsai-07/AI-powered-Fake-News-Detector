/**
 * ResultCard Component
 * Displays the prediction result with visual indicators.
 */

function ResultCard({ result }) {
  const { prediction, confidence } = result;
  const isFake = prediction === "Fake";
  const isUncertain = prediction === "Uncertain";
  const confidencePercent = Math.round(confidence * 100);

  return (
    <div
      className={`result-card ${isFake ? "result-fake" : isUncertain ? "result-uncertain" : "result-real"}`}
    >
      <div className="result-header">
        <span className="result-icon">
          {isFake ? "⚠️" : isUncertain ? "🤔" : "✅"}
        </span>
        <h2 className="result-title">Analysis Result</h2>
      </div>

      <div className="result-body">
        <div className="prediction-badge">
          <span
            className={`badge ${isFake ? "badge-fake" : isUncertain ? "badge-uncertain" : "badge-real"}`}
          >
            {prediction}
          </span>
        </div>

        <div className="confidence-section">
          <div className="confidence-header">
            <span>Confidence</span>
            <span className="confidence-value">{confidencePercent}%</span>
          </div>
          <div className="confidence-bar">
            <div
              className={`confidence-fill ${isFake ? "fill-fake" : isUncertain ? "fill-uncertain" : "fill-real"}`}
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>

        <p className="result-description">
          {isFake ? (
            <>
              Our AI model indicates this content may contain{" "}
              <strong>misleading or false information</strong>. We recommend
              verifying with trusted sources.
            </>
          ) : isUncertain ? (
            <>
              Our AI model is <strong>uncertain</strong> about this content. The
              prediction confidence is low, so please verify with multiple
              reliable sources.
            </>
          ) : (
            <>
              Our AI model indicates this content appears to be{" "}
              <strong>credible and reliable</strong>. However, always
              cross-reference important information.
            </>
          )}
        </p>
      </div>

      <div className="result-footer">
        <p className="disclaimer">
          ⚠️ This is an AI-based prediction and should be used as a reference
          only. Always verify information from multiple reliable sources.
        </p>
      </div>
    </div>
  );
}

export default ResultCard;
