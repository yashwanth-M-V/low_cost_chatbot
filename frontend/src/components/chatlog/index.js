// src/components/ChatLog/index.js
import React, { useEffect, useRef } from 'react';
import Message from './message';
import './chatlog.css';

function ChatLog({ messages }) {
  const messagesEndRef = useRef(null);

  // Scroll to the bottom of the chat log when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-log">
      {messages.map((msg) => (
        <Message key={msg.id} type={msg.type} text={msg.text} />
      ))}
      <div ref={messagesEndRef} /> {/* Invisible div to scroll to */}
    </div>
  );
}

export default ChatLog;