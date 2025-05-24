// src/components/InputBar/index.js
import React, { useState, useRef, useEffect } from 'react';
import './inputbar.css';

function InputBar({ onSendMessage, isLoading }) {
  const [inputText, setInputText] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText);
      setInputText(''); // Clear input after sending
      inputRef.current.focus(); // Focus input immediately after clearing
    }
  };

  // Auto-focus when input becomes enabled (isLoading changes to false)
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  return (
    <form className="input-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        className="input-field"
        placeholder="Type your message here..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        disabled={isLoading}
        ref={inputRef} // Attach the ref to the input
      />
      <button type="submit" className="send-button" disabled={isLoading}>
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}

export default InputBar;