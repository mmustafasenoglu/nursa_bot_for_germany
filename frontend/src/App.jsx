import React, { useState, useRef, useEffect } from 'react';
import { Send, Menu, X } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatMessage from './components/ChatMessage';
import RightsModal from './components/RightsModal';
import { askQuestion } from './api';

function App() {
  const [language, setLanguage] = useState('de');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRightsModalOpen, setIsRightsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const quickQuestions = {
    de: [
      "Wie lange dauert die Pflegeausbildung?",
      "Welches Sprachniveau brauche ich?",
      "Wie viel verdiene ich während der Ausbildung?",
      "Was sind die Aufgaben einer Pflegefachkraft?",
      "Wie läuft die Abschlussprüfung ab?",
      "Was bedeutet 'Anerkennung' ausländischer Abschlüsse?",
      "Wie messe ich den Blutdruck richtig?",
      "Was ist die 5-R-Regel bei der Medikamentengabe?"
    ],
    en: [
      "How long does the nursing Ausbildung take?",
      "What German language level do I need?",
      "How much do I earn during training?",
      "What are the duties of a nurse?",
      "How does the nursing exam work?",
      "What is Anerkennung (recognition of foreign diplomas)?",
      "How do I measure blood pressure correctly?",
      "What are the 5 rights of medication safety?"
    ]
  };

  const handleSend = async (text) => {
    if (!text.trim()) return;

    const newMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const answer = await askQuestion(text, language);
      setMessages((prev) => [...prev, { role: 'bot', content: answer }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'bot', content: language === 'de' ? 'Ein Fehler ist aufgetreten.' : 'An error occurred.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend(input);
    }
  };

  return (
    <div className="app-container">
      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div className="mobile-overlay" onClick={() => setIsSidebarOpen(false)}></div>
      )}

      <Sidebar 
        language={language} 
        setLanguage={setLanguage} 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      
      <main className="chat-area">
        <header className="chat-header">
          <div className="header-left">
            <button className="menu-btn" onClick={() => setIsSidebarOpen(true)}>
              <Menu size={24} />
            </button>
            <h1>PflegeKompassAI</h1>
          </div>
          <button 
            className="header-btn"
            onClick={() => setIsRightsModalOpen(true)}
          >
            {language === 'de' ? '⚖️ Meine Rechte' : '⚖️ My Rights'}
          </button>
        </header>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🩺</div>
              <h2 className="empty-title">
                {language === 'de' 
                  ? 'Willkommen bei PflegeKompassAI' 
                  : 'Welcome to PflegeKompassAI'}
              </h2>
              <div className="quick-questions-grid">
                {quickQuestions[language].map((q, idx) => (
                  <button 
                    key={idx} 
                    className="quick-btn"
                    onClick={() => handleSend(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <ChatMessage key={idx} role={msg.role} content={msg.content} />
              ))}
              {isLoading && (
                <div className="message-row bot">
                  <div className="bot-avatar">🩺</div>
                  <div className="message-bubble">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="input-container">
          <div className="input-box">
            <input
              type="text"
              placeholder={language === 'de' ? 'Frage mich alles...' : 'Ask me anything...'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button 
              className="send-btn" 
              onClick={() => handleSend(input)}
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </main>

      <RightsModal 
        isOpen={isRightsModalOpen} 
        onClose={() => setIsRightsModalOpen(false)} 
        language={language} 
      />
    </div>
  );
}

export default App;
