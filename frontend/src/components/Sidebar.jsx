import { X } from 'lucide-react';

const Sidebar = ({ language, setLanguage, isOpen, onClose, onClearChat }) => {
  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2>🩺 NurseMate AI</h2>
        <button className="close-btn-mobile" onClick={onClose}>
          <X size={24} />
        </button>
      </div>
      
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
        <h3>📖 {language === 'de' ? 'Über NurseMate AI' : 'About NurseMate AI'}</h3>
        <div className="about-text">
          {language === 'de' ? (
            <>
              <p>Hilft Pflegeauszubildenden in Deutschland, schnell Antworten zu finden.</p>
              <ul>
                <li>Ausbildungsstruktur & Bewerbung</li>
                <li>Vitalzeichen & klinische Grundlagen</li>
                <li>Medikamentengabe (5-R-Regel)</li>
                <li>Hygiene & Infektionsschutz</li>
                <li>Pflegedokumentation</li>
                <li>Notfallsituationen</li>
              </ul>
            </>
          ) : (
            <>
              <p>Helps nursing students in Germany quickly find answers.</p>
              <ul>
                <li>Training structure & application</li>
                <li>Vital signs & clinical basics</li>
                <li>Medication administration (5 Rights)</li>
                <li>Hygiene & infection control</li>
                <li>Nursing documentation</li>
                <li>Emergency situations</li>
              </ul>
            </>
          )}
        </div>
      </div>
      
      <button className="clear-btn" onClick={onClearChat}>
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
