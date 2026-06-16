import React from 'react';

const RightsModal = ({ isOpen, onClose, language }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2>{language === 'de' ? '⚖️ Meine Rechte' : '⚖️ My Rights'}</h2>
        <div className="modal-body">
          {language === 'de' ? (
            <>
              <p>Als Pflegekraft in Deutschland haben Sie bestimmte grundlegende Rechte:</p>
              <ul>
                <li><strong>Faire Vergütung:</strong> Recht auf Mindestlohn und tarifliche Bezahlung.</li>
                <li><strong>Arbeitszeiten:</strong> Einhaltung der gesetzlichen Arbeits- und Pausenzeiten.</li>
                <li><strong>Urlaub:</strong> Gesetzlicher Anspruch auf bezahlten Erholungsurlaub.</li>
                <li><strong>Krankheit:</strong> Anspruch auf Lohnfortzahlung im Krankheitsfall.</li>
                <li><strong>Schutz:</strong> Schutz vor Diskriminierung und ein sicheres Arbeitsumfeld.</li>
              </ul>
              <p>Für detaillierte rechtliche Beratung wenden Sie sich bitte an eine Gewerkschaft (z.B. ver.di) oder einen Rechtsanwalt.</p>
            </>
          ) : (
            <>
              <p>As a nursing professional in Germany, you have certain fundamental rights:</p>
              <ul>
                <li><strong>Fair Compensation:</strong> Right to minimum wage and collective agreement pay.</li>
                <li><strong>Working Hours:</strong> Compliance with legal working and break times.</li>
                <li><strong>Vacation:</strong> Legal right to paid recreational leave.</li>
                <li><strong>Illness:</strong> Right to continued pay in case of illness.</li>
                <li><strong>Protection:</strong> Protection against discrimination and a safe working environment.</li>
              </ul>
              <p>For detailed legal advice, please contact a union (e.g., ver.di) or a lawyer.</p>
            </>
          )}
        </div>
        <button className="close-btn" onClick={onClose}>
          {language === 'de' ? 'Schließen' : 'Close'}
        </button>
      </div>
    </div>
  );
};

export default RightsModal;
