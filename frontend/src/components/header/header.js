// src/components/Header/index.js
import React from 'react';
import Logo from './logo';
import HamburgerMenu from './hamburgermenu';
import './header.css';

function Header() {
  const handleMenuToggle = () => {
    console.log('Hamburger menu toggled!');
    // Implement your menu open/close logic here (e.g., using state in App.js or a global state management)
  };

  return (
    <header className="header">
      <Logo />
      <h1 className="header-title">Low-Cost Chatbot</h1>
      <HamburgerMenu onToggle={handleMenuToggle} />
    </header>
  );
}

export default Header;