// src/components/Header/HamburgerMenu.js
import React from 'react';

function HamburgerMenu({ onToggle }) {
  return (
    <button className="hamburger-menu" onClick={onToggle} aria-label="Toggle menu">
      <div className="hamburger-bar"></div>
      <div className="hamburger-bar"></div>
      <div className="hamburger-bar"></div>
    </button>
  );
}

export default HamburgerMenu;