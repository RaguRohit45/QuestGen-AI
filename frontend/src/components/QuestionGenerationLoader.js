import React from 'react';
import './QuestionGenerationLoader.css';

const QuestionGenerationLoader = ({ count }) => {
  return (
    <div className="question-generation-loader">
      <div className="loader-content">
        <div className="loader-spinner"></div>
        <h3>Generating {count} Questions</h3>
        <p>This may take a few moments as we're carefully crafting your questions...</p>
        <div className="loader-details">
          <div className="loader-detail-item">
            <span className="loader-detail-icon">⚡</span>
            <span>Analyzing question patterns</span>
          </div>
          <div className="loader-detail-item">
            <span className="loader-detail-icon">🧠</span>
            <span>Generating unique questions</span>
          </div>
          <div className="loader-detail-item">
            <span className="loader-detail-icon">✅</span>
            <span>Validating question quality</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionGenerationLoader;
