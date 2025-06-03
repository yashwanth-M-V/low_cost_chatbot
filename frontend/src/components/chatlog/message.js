// src/components/ChatLog/message.js
import React from 'react';
import userIcon from '../../assets/user-icon.png'; // Correct path from message.js to src/assets
import botIcon from '../../assets/bot-icon.png';   // Correct path from message.js to src/assets

function Message({ type, text }) {
  const isUser = type === 'user';
  const isBot = type === 'bot';
  const isError = type === 'error'; // For displaying error messages within chat

  let iconSrc;
  if (isUser) {
    iconSrc = userIcon;
  } else if (isBot) {
    iconSrc = botIcon;
  }
  // For error messages, you might choose not to show an icon or use a specific error icon

  return (
    <div className={`message-container ${type}`}>
      {iconSrc && <img src={iconSrc} alt={`${type} icon`} className="message-icon" />}
      <div className="message-bubble">
        {isError ? <span className="message-error-text">Error: {text}</span> : text}
      </div>
    </div>
  );
}

export default Message;