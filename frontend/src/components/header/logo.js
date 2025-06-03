// src/components/Header/Logo.js
import React from 'react';
import logoImage from '../../assets/logo.png'; // Correct path from Header/Logo.js to src/assets

function Logo() {
  return (
    <div className="logo">
      <img src={logoImage} alt="Chatbot Logo" className="logo-image" />
    </div>
  );
}

export default Logo;