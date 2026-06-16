import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ role, content }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      {!isUser && (
        <div className="bot-avatar">
          🩺
        </div>
      )}
      <div className="message-bubble">
        {isUser ? (
          content
        ) : (
          <ReactMarkdown>{content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
