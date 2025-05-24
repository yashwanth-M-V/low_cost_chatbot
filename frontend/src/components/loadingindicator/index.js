// src/components/LoadingIndicator/index.js
import React from 'react';
import './loadingindicator.css';

function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="spinner"></div>
      <p>Thinking...</p>
    </div>
  );
}

export default LoadingIndicator;




