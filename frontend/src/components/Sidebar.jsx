import React from 'react';

const Sidebar = ({ language, setLanguage }) => {
  return (
    <div className="sidebar">
      <h2>🩺 PflegeKompassAI</h2>
      
      <div className="sidebar-section lang-section">
        <h3>🌐 {language === 'de' ? 'Sprache' : 'Language'}</h3>
        <div className="lang-toggle">
          <button 
            className={`lang-btn ${language === 'de' ? 'active' : ''}`}
            onClick={() => setLanguage('de')}
          >
            🇩🇪 DE
          </button>
          <button 
            className={`lang-btn ${language === 'en' ? 'active' : ''}`}
            onClick={() => setLanguage('en')}
          >
            🇬🇧 EN
          </button>
        </div>
      </div>

      <div className="sidebar-section">
        <h3>📖 {language === 'de' ? 'Über PflegeKompassAI' : 'About PflegeKompassAI'}</h3>
        <div className="about-text">
          {language === 'de' ? (
            <>
              <p>Hilft Pflegeauszubildenden in Deutschland, schnell Antworten zu finden.</p>
              <ul>
                <li>Ausbildungsstruktur</li>
                <li>Vitalzeichen</li>
                <li>Medikamentengabe</li>
              </ul>
            </>
          ) : (
            <>
              <p>Helps nursing students in Germany quickly find answers.</p>
              <ul>
                <li>Training structure</li>
                <li>Vital signs</li>
                <li>Medication administration</li>
              </ul>
            </>
          )}
        </div>
      </div>
      
      <button className="clear-btn" onClick={() => window.location.reload()}>
        🗑️ {language === 'de' ? 'Chat leeren' : 'Clear Chat'}
      </button>

      <div className="sidebar-footer" style={{ marginTop: '1.5rem', fontSize: '0.75rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        {language === 'de' ? 'Entwickelt von' : 'Developed by'}<br />
        <strong>Mustafa Şenoğlu & Müslüm Evin</strong>
      </div>
    </div>
  );
};

export default Sidebar;
