import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/header/header';
import ChatLog from './components/chatlog';
import InputBar from './components/inputbar/inputbar';
import ErrorBoundary from './components/errorboundary';
import LoadingIndicator from './components/loadingindicator';
import './App.css';

// Configure API client
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const newUserMessage = { id: Date.now(), type: 'user', text: text };
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/v1/chat/chat', {
        message: text
      });

      const newBotMessage = { 
        id: Date.now() + 1, 
        type: 'bot', 
        text: response.data.response,
        meta: {
          tokens: response.data.tokens_used,
          speed: response.data.tokens_per_sec
        }
      };
      setModelStatus(response.data.model_status);
      setMessages(prev => [...prev, newBotMessage]);

    } catch (err) {
      console.error("API Error:", err);
      const errorMessage = err.response?.data?.detail || 'Failed to communicate with the chatbot service';
      setError(errorMessage);
      setMessages(prev => [...prev, { 
        id: Date.now() + 1, 
        type: 'error', 
        text: `Error: ${errorMessage}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.get('/api/health');
        setModelStatus(response.data.model_status);
      } catch (err) {
        console.error("Health check failed:", err);
      }
    };

    checkHealth();
    setMessages([{ id: 1, type: 'bot', text: 'Hello! How can I help you today?' }]);
  }, []);

  return (
    <ErrorBoundary>
      <div className="App">
        <Header status={modelStatus} />
        <main className="App-main">
          <ChatLog messages={messages} />
          {isLoading && <LoadingIndicator />}
          {error && <div className="App-error-message">{error}</div>}
        </main>
        <InputBar 
          onSendMessage={handleSendMessage} 
          isLoading={isLoading}
          maxLength={500}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;