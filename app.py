"""
app.py — PflegeKompassAI Streamlit Arayüzü
Hemşirelik Ausbildung öğrencileri için bilingual (DE/EN) chatbot
"""

import streamlit as st
import os
import datetime
import subprocess
from rag_pipeline import ask

# ── FAISS Index Yoksa Otomatik Oluştur ─────────────────────────────────────────
FAISS_INDEX_PATH = "./faiss_index"
if not os.path.exists(FAISS_INDEX_PATH):
    with st.spinner("🔄 Setting up knowledge base... (~1 minute)"):
        try:
            subprocess.run(["python", "ingest.py"], check=True, capture_output=True)
            st.success("✅ Knowledge base ready!")
            st.rerun()
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Setup failed: {e.stderr.decode()}")
            st.stop()

# ── Sayfa Yapılandırması ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PflegeKompassAI — KI-Assistent für die Pflegeausbildung",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Streamlit gürültüsünü tamamen temizle ── */
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stStatusWidget"],
    .stDeployButton { display: none !important; }

    /* ── Sıfır padding / margin ve Bouncing (Rubber-banding) engelle ── */
    html, body { 
        margin: 0; 
        padding: 0; 
        overscroll-behavior: none; /* Sayfanın en üstünde/altında sekmesini engeller */
    }
    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, #eef6fc 100%) !important;
        font-family: 'Inter', sans-serif;
        color: #2b2b2b;
        min-height: 100dvh;
    }
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 6rem !important;  /* chat input icin yer */
        max-width: 820px;
    }
    
    /* Streamlit chat input container'i yukarı it, footer'a yer aç */
    div[data-testid="stBottom"] {
        bottom: 52px !important;
        background: transparent !important;
    }
    
    /* Eski stChatInput push'unu siliyoruz ki sadece stBottom itilsin */
    div[data-testid="stChatInput"] {
        bottom: 0 !important;
    }
    
    /* Streamlit Cloud'daki chat input kullanıcı profil fotoğrafını gizle */
    div[data-testid="stChatInput"] img {
        display: none !important;
    }
    
    /* Streamlit'in section üst padding'i */
    section[data-testid="stMain"] > div:first-child {
        padding-top: 0 !important;
    }

    /* ──── NAVBAR ──── */
    /* stHorizontalBlock icinde nav-marker varsa, o satiri navbar yap */
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) {
        background: #ffffff;
        border: 1px solid #e8eaed;
        border-radius: 14px;
        padding: 0.5rem 1.2rem;
        margin: 0.4rem 0 0.8rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
        align-items: center;
    }
    .nm-brand {
        display: flex;
        align-items: baseline;
        gap: 0.4rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-top: 0.3rem;
    }
    .nm-brand-tag {
        font-size: 0.75rem;
        font-weight: 400;
        color: #999;
        white-space: nowrap;
    }

    /* Nav buton container */
    div[data-testid="stHorizontalBlock"]:has(.nav-marker) [data-testid="stColumn"] {
        padding: 0 4px !important;
        min-width: 0;
    }

    /* Navbar butonlarını pill şekline getir */
    div[data-testid="stHorizontalBlock"]:has(> div > div[data-testid="stColumn"] > div > div > div[data-testid="stButton"] > button[kind="secondary"])
    { /* targeting only nav buttons via column layout */ }

    /* Nav buton stilleri — key ile hedefle */
    button[data-testid="baseButton-secondary"][kind="secondary"]:is([id*="nav_"]),
    button[data-testid="baseButton-primary"][kind="primary"]:is([id*="nav_"]) {
        border-radius: 99px !important;
        padding: 0.2rem 0.85rem !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        min-height: unset !important;
        height: 30px !important;
        line-height: 1 !important;
    }
    /* Nav buton container */
    .nm-nav-btns {
        display: flex;
        align-items: center;
        gap: 4px;
        background: #f4f5f7;
        border-radius: 99px;
        padding: 3px;
        border: 1px solid rgba(0,0,0,0.07);
    }
    /* ──── NAVBAR ──── */

    /* ──── CHAT BALONCUKLARI ──── */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 1.2rem 0;
    }
    .user-bubble {
        background: #f1f3f4;
        color: #1f1f1f;
        padding: 0.75rem 1.1rem;
        border-radius: 22px 22px 4px 22px;
        max-width: 80%;
        font-size: 0.97rem;
        line-height: 1.5;
    }
    .bot-message {
        display: flex;
        justify-content: flex-start;
        margin: 1.2rem 0;
        gap: 0.8rem;
        align-items: flex-start;
    }
    .bot-avatar { font-size: 1.6rem; flex-shrink: 0; margin-top: 0.1rem; }
    .bot-bubble {
        color: #1f1f1f;
        padding: 0.3rem 0;
        max-width: 90%;
        font-size: 0.97rem;
        line-height: 1.65;
    }
    .chat-container { padding: 0; }

    /* ──── BOŞ DURUM ──── */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 22vh;
        padding: 2rem 0 1rem 0;
        text-align: center;
    }
    .empty-state-greeting {
        font-size: 2rem;
        font-weight: 500;
        line-height: 1.3;
        background: linear-gradient(135deg, #1f1f1f 0%, #4a6fa5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    /* ──── FOOTER (sadece PC — fixed bottom) ──── */
    .nm-footer {
        position: fixed;
        bottom: 0;             /* En alta yapışık */
        left: 0;
        right: 0;
        height: 52px;          /* Sabit yükseklik - daha kalın */
        z-index: 99999;
        background: #ffffff;
        border-top: 1px solid #e8eaed;
        padding: 0 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .nm-footer-left {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.74rem;
        color: #aaa;
    }
    .nm-footer-left strong { color: #555; font-weight: 600; }
    .nm-footer-sep { color: #d0d0d0; }
    .nm-footer-right {
        font-size: 0.74rem;
        color: #aaa;
        white-space: nowrap;
    }
    .nm-footer-right strong { color: #555; font-weight: 600; }
    .nm-footer-heart { color: #e74c3c; }
    /* ── eski sınıflar artık kullanılmıyor ── */
    .nm-footer-col ul li {
        font-size: 0.73rem;
        color: #6e7681;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .nm-footer-col ul li::before {
        content: '';
        width: 3px; height: 3px;
        border-radius: 50%;
        background: #1a73e8;
        flex-shrink: 0;
        opacity: 0.8;
    }
    .nm-footer-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin: 0 0 1rem 0;
    }
    .nm-footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nm-footer-copy { font-size: 0.7rem; color: #484f58; }
    .nm-footer-credits { font-size: 0.7rem; color: #484f58; }
    .nm-footer-credits strong { color: #6e7681; font-weight: 600; }

    /* ── MOBİL ── */
    @media (max-width: 768px) {
        /* Mobilde navbar'i gizlemek yerine kolonlarin alt alta dusmesini (stack) engelle */
        div[data-testid="stHorizontalBlock"]:has(.nav-marker) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            padding: 0.4rem 0.5rem !important;
            gap: 0.3rem !important;
        }
        
        /* Logo sutunu biraz buyuk, boslugu (2. sutun) gizle */
        div[data-testid="stHorizontalBlock"]:has(.nav-marker) > div[data-testid="stColumn"]:nth-child(1) { flex: 3 !important; }
        div[data-testid="stHorizontalBlock"]:has(.nav-marker) > div[data-testid="stColumn"]:nth-child(2) { display: none !important; }
        div[data-testid="stHorizontalBlock"]:has(.nav-marker) > div[data-testid="stColumn"]:nth-child(3) { flex: 1 !important; }
        div[data-testid="stHorizontalBlock"]:has(.nav-marker) > div[data-testid="stColumn"]:nth-child(4) { flex: 1 !important; }

        .nm-brand { font-size: 0.95rem; margin-top: 0.1rem; }
        .nm-brand-tag { display: none; } /* Mobilde "KI-Assistent" alt basligini gizle */

        /* Mobilde butonlari kucult */
        button[data-testid="baseButton-secondary"][kind="secondary"]:is([id*="nav_"]),
        button[data-testid="baseButton-primary"][kind="primary"]:is([id*="nav_"]) {
            padding: 0.1rem 0.2rem !important;
            font-size: 0.65rem !important;
            height: 26px !important;
        }

        /* Mobilde footer'i goster ama kucult */
        .nm-footer {
            height: 40px;
            padding: 0 0.8rem;
        }
        /* Logodaki uzun yaziyi gizle */
        .nm-footer-desc, .nm-footer-copy, .nm-footer-sep {
            display: none !important;
        }
        .nm-footer-right {
            font-size: 0.68rem;
            text-align: right;
            line-height: 1.2;
        }
        .nm-footer-left {
            font-size: 0.95rem;
        }
        /* Chat input container'i mobilde yeni footer boyuna gore ayarla ve ic boslugu (padding) kaldir */
        div[data-testid="stBottom"] {
            bottom: 40px !important;
            padding-bottom: 0 !important;
        }

        .empty-state { min-height: 10vh; padding: 1rem 0; }
        .empty-state-greeting { font-size: 1.65rem; }
        .user-bubble, .bot-bubble { max-width: 95%; font-size: 0.93rem; }
        
        /* Icerigin en alta kadar kayabilmesi icin boslugu artir */
        .main .block-container { padding: 0 0.3rem 7.5rem 0.3rem !important; }
    }
</style>
""", unsafe_allow_html=True)


# ── Dil Metinleri ──────────────────────────────────────────────────────────────
TEXTS = {
    "de": {
        "placeholder": "Frage mich alles über die Pflegeausbildung...",
        "clear": "🗑️ Chat leeren",
        "quick_label": "Häufige Fragen",
        "empty_title": "Willkommen bei PflegeKompassAI,<br>Wie kann ich helfen?",
        "thinking": "PflegeKompassAI denkt nach...",
        "tagline": "KI-Assistent für die Pflegeausbildung",
        "quick_answer_prefix": "⚡ **Schnelle Antwort:**\n\n",
        "quick_questions": [
            {"q": "Wie lange dauert die Pflegeausbildung?", "a": "Die generalistische Pflegeausbildung zur Pflegefachfrau / zum Pflegefachmann dauert in Deutschland in der Regel **3 Jahre** in Vollzeit. Die Ausbildung ist dual aufgebaut: Sie wechseln blockweise zwischen dem theoretischen Unterricht an einer Pflegeschule und praktischen Einsätzen in verschiedenen Einrichtungen (Krankenhaus, Pflegeheim, ambulante Pflege).\n\nWenn Sie die Ausbildung in Teilzeit absolvieren, kann sie bis zu **5 Jahre** dauern. Insgesamt umfasst der Lehrplan gesetzlich vorgeschriebene 2.100 Stunden theoretischen Unterricht und 2.500 Stunden praktische Ausbildung."},
            {"q": "Welches Sprachniveau brauche ich?", "a": "Für den Beginn einer Pflegeausbildung in Deutschland benötigen Sie grundsätzlich **Sprachniveau B2** in Deutsch (nach dem GER). Dies ist eine formelle und praktische Voraussetzung, da Sie komplexe medizinische Anweisungen verstehen, sicher mit Patienten kommunizieren, Pflegedokumentationen verfassen und die staatlichen Abschlussprüfungen auf Deutsch bestehen müssen.\n\nEinige wenige Pflegeschulen akzeptieren Bewerber mit einem starken B1-Niveau, sofern diese sich verpflichten, ausbildungsbegleitende Intensivsprachkurse zu besuchen. Für die spätere Berufszulassung ist B2 jedoch der verbindliche Standard."},
            {"q": "Wie viel verdiene ich während der Ausbildung?", "a": "Pflegeauszubildende in Deutschland erhalten eine monatliche Ausbildungsvergütung. Wenn Ihr Träger an den Tarifvertrag für den öffentlichen Dienst (TVAöD-Pflege) gebunden ist, liegt das Bruttogehalt aktuell bei etwa:\n- **1. Ausbildungsjahr:** ca. 1.340 €\n- **2. Ausbildungsjahr:** ca. 1.400 €\n- **3. Ausbildungsjahr:** ca. 1.500 €\n\nPrivate Kliniken oder kirchliche Träger (wie Caritas oder Diakonie) haben eigene Verträge (z.B. AVR), die Vergütung ist aber meist sehr ähnlich. Zusätzlich erhalten Sie Zuschläge für Schicht-, Wochenend- und Feiertagsdienste."},
            {"q": "Was sind die Aufgaben einer Pflegefachkraft?", "a": "Als examinierte Pflegefachkraft in Deutschland haben Sie ein sehr vielfältiges Aufgabengebiet, das eigenverantwortliche pflegerische und ärztlich delegierte medizinische Tätigkeiten umfasst. Zu den Hauptaufgaben gehören:\n- **Grundpflege:** Unterstützung der Patienten bei Körperpflege, Mobilität und Nahrungsaufnahme.\n- **Behandlungspflege:** Medikamentengabe, Verbandswechsel, Richten von Infusionen und Blutentnahmen (auf ärztliche Anordnung).\n- **Monitoring:** Kontrolle und Überwachung der Vitalparameter (Blutdruck, Puls, Temperatur, Atmung).\n- **Pflegedokumentation:** Lückenlose rechtssichere Aufzeichnung aller Pflegemaßnahmen und des Patientenstatus.\n- **Kommunikation:** Wichtiges Bindeglied zwischen Ärzten, Patienten, Therapeuten und Angehörigen."},
            {"q": "Wie läuft die Abschlussprüfung ab?", "a": "Das Staatsexamen am Ende der 3-jährigen Ausbildung ist sehr anspruchsvoll und besteht aus drei Teilen, die alle bestanden werden müssen:\n1. **Schriftliche Prüfung:** Drei Klausuren, die Pflegeprozesse, Krankheitslehre, rechtliche Rahmenbedingungen und Pflegewissenschaften abdecken.\n2. **Praktische Prüfung:** Sie übernehmen auf einer Station eigenverantwortlich die komplette Pflege einer Patientengruppe für mehrere Stunden. Sie planen, führen durch und dokumentieren, während Fachprüfer Sie beobachten und bewerten.\n3. **Mündliche Prüfung:** Ein Fachgespräch über komplexe Pflegesituationen, Anatomie/Physiologie und berufsethische Fragen."},
            {"q": "Was bedeutet 'Anerkennung' ausländischer Abschlüsse?", "a": "Die 'Anerkennung' ist das offizielle behördliche Verfahren, bei dem ein im Ausland erworbener Pflegeabschluss mit dem deutschen Ausbildungsstandard verglichen wird. Nur mit einer erfolgreichen Anerkennung erhalten Sie die staatliche Erlaubnis zur Führung der Berufsbezeichnung 'Pflegefachkraft'.\n\nWerden wesentliche Unterschiede festgestellt (was häufig der Fall ist), erhalten Sie einen Defizitbescheid. Sie müssen dann entweder einen **Anpassungslehrgang** absolvieren oder eine **Kenntnisprüfung** ablegen, um die volle Berufszulassung (die 'Urkunde') zu erhalten."},
            {"q": "Wie messe ich den Blutdruck richtig?", "a": "Die korrekte Blutdruckmessung (RR-Messung) nach Riva-Rocci ist ein klinischer Standard. Die Schritte sind:\n1. **Vorbereitung:** Der Patient sollte sich 3–5 Minuten ausruhen. Die Messung erfolgt meist im Sitzen, der Arm muss entspannt auf Herzhöhe gelagert sein.\n2. **Manschette anlegen:** Die Manschette (in passender Größe) wird am entblößten Oberarm angelegt, ca. 2–3 cm oberhalb der Ellenbeuge.\n3. **Palpatorisch vorfühlen:** Radialispuls tasten, Manschette aufpumpen bis der Puls verschwindet (systolischer Schätzwert) und dann 30 mmHg höher pumpen.\n4. **Auskultation:** Stethoskop auf die Arteria brachialis setzen. Druck langsam ablassen (2–3 mmHg pro Sekunde).\n5. **Ablesen:** Das erste pochende Geräusch (Korotkoff I) ist der **systolische** Wert, das vollständige Verschwinden der Geräusche (Korotkoff V) ist der **diastolische** Wert."},
            {"q": "Was ist die 5-R-Regel bei der Medikamentengabe?", "a": "Die 5-R-Regel ist ein essenzieller Sicherheitsstandard in der Pflege, um Medikationsfehler zu vermeiden. Vor jeder Medikamentengabe müssen 5 Punkte zwingend kontrolliert werden:\n1. **Richtiger Patient:** Name und Geburtsdatum abgleichen.\n2. **Richtiges Medikament:** Präparat mit der ärztlichen Anordnung vergleichen.\n3. **Richtige Dosierung:** Konzentration und Menge genau prüfen.\n4. **Richtige Applikationsform:** Überprüfen, wie das Medikament verabreicht werden soll (z.B. oral, i.v., s.c.).\n5. **Richtiger Zeitpunkt:** Gabe zum vorgeschriebenen Intervall/Uhrzeit.\n*(Hinweis: In der modernen Pflegepraxis wird oft auch die 6-R-Regel gelehrt, bei der als 6. Punkt die 'Richtige Dokumentation' hinzukommt).*"},
        ],
        "sidebar_lang": "🌐 Sprache",
        "sidebar_about_title": "📖 Über PflegeKompassAI",
        "sidebar_about": """
**PflegeKompassAI** hilft Pflegeauszubildenden in Deutschland, schnell Antworten auf Fragen zur Ausbildung, zu klinischen Grundlagen und zum Pflegealltag zu finden.

**Warum wurde es entwickelt?**
Viele internationale Pflegestudierende kämpfen mit der deutschen Sprachbarriere und dem komplexen Ausbildungssystem. PflegeKompassAI überbrückt diese Lücke — auf Deutsch und Englisch, kostenlos.

**Themen:**
- 🏥 Ausbildungsstruktur & Bewerbung
- 🩺 Vitalzeichen & klinische Grundlagen
- 💊 Medikamentengabe (5-R-Regel)
- 🧼 Hygiene & Infektionsschutz
- 📋 Pflegedokumentation
- 🚨 Notfallsituationen
        """,
        "sidebar_clear": "🗑️ Chat leeren",
        # footer
        "f_desc": "KI-Chatbot für Pflegeauszubildende in Deutschland — beantwortet Fragen zu Ausbildung, klinischen Grundlagen und Medikamentengabe auf Deutsch und Englisch.",
        "f_c1": "Technologien",
        "f_c2": "Themen",
        "f_c3": "Über das Projekt",
        "f_topics": ["Ausbildungsstruktur", "Vitalzeichen & Klinik", "Hygiene & Infektionsschutz", "Medikamentengabe", "Pflegedokumentation", "Notfallsituationen"],
        "f_about": ["Für internationale Pflegestudierende", "Überbrückt Sprach- & Wissensbarrieren", "Kostenlos & offen zugänglich", "v1.0 — aktiv in Entwicklung"],
        "f_copy": "© {year} PflegeKompassAI. Alle Rechte vorbehalten.",
        "f_by": "Entwickelt von",
    },
    "en": {
        "placeholder": "Ask me anything about nursing training in Germany...",
        "clear": "🗑️ Clear Chat",
        "quick_label": "Quick Questions",
        "empty_title": "Welcome to PflegeKompassAI,<br>How can I help you?",
        "thinking": "PflegeKompassAI is thinking...",
        "tagline": "Nursing Ausbildung Assistant",
        "quick_answer_prefix": "⚡ **Quick Answer:**\n\n",
        "quick_questions": [
            {"q": "How long does the nursing Ausbildung take?", "a": "The generalist nursing training (Ausbildung zur Pflegefachkraft) in Germany typically takes **3 years** when completed full-time. During this time, you will alternate between theoretical blocks at a nursing school (Pflegeschule) and practical assignments in various clinical settings (such as hospitals, nursing homes, and outpatient care).\n\nIf you choose to do the training part-time, it can take up to **5 years**. The total curriculum includes exactly 2,100 hours of theoretical classroom instruction and 2,500 hours of practical training."},
            {"q": "What German language level do I need?", "a": "To start a nursing Ausbildung in Germany, you generally need a **B2 level in German** (according to the CEFR). This is a legal and practical requirement because you must be able to understand medical instructions, communicate effectively with patients, write nursing documentation, and pass the final state exams in German.\n\nSome nursing schools or hospitals might accept applicants with a strong B1 level if they commit to taking intensive language courses before or during the first months of training, but B2 is the official standard for professional recognition."},
            {"q": "How much do I earn during training?", "a": "Nursing trainees in Germany receive a monthly salary (Ausbildungsvergütung) from their employer. If your hospital is bound by public service collective agreements (TVAöD-Pflege), your approximate gross monthly salary will be:\n- **1st Year:** ~ €1,340\n- **2nd Year:** ~ €1,400\n- **3rd Year:** ~ €1,500\n\nPrivate hospitals or church-run institutions (like Caritas or Diakonie) have their own collective agreements (AVR), but they generally pay very similar amounts. You will also receive extra pay for working shifts, weekends, or holidays."},
            {"q": "What are the duties of a nurse?", "a": "As a registered nurse (Pflegefachkraft) in Germany, your responsibilities are highly diverse and combine both independent nursing tasks and delegated medical tasks. Key duties include:\n- **Basic Care (Grundpflege):** Assisting patients with personal hygiene, mobility, and nutrition.\n- **Medical Treatment Care (Behandlungspflege):** Administering medication, changing wound dressings, setting up IV lines, and taking blood samples (as prescribed by a doctor).\n- **Monitoring:** Checking vital signs (blood pressure, pulse, temperature) and observing the patient's general condition.\n- **Documentation:** Meticulously recording all care activities, medications given, and the patient's progress.\n- **Communication:** Acting as the primary link between patients, doctors, and relatives."},
            {"q": "How does the nursing exam work?", "a": "The final state examination (Staatsexamen) at the end of your 3-year Ausbildung consists of three separate parts, and you must pass all of them to become a registered nurse:\n1. **Written Exam:** Three exams covering nursing situations, clinical basics, and legal/institutional frameworks.\n2. **Practical Exam:** A real-life scenario where you are assigned a group of patients. You must independently plan, execute, and document their care over a few hours while examiners observe and evaluate you.\n3. **Oral Exam:** Usually covers complex nursing scenarios, ethics, anatomy, and disease pathology, where you defend your clinical reasoning."},
            {"q": "What is Anerkennung (recognition of foreign diplomas)?", "a": "'Anerkennung' is the official legal process of evaluating a nursing qualification obtained outside of Germany to determine if it is equivalent to the German standard.\nIf your education is not fully equivalent, you will receive a deficit notice (Defizitbescheid) and must complete adaptation measures (Anpassungslehrgang) or pass a knowledge test (Kenntnisprüfung). Once successfully completed, you receive your 'Urkunde' (professional license), allowing you to legally work as a 'Pflegefachkraft' in Germany."},
            {"q": "How do I measure blood pressure correctly?", "a": "Measuring blood pressure (RR-Messung) correctly is a vital clinical skill. According to clinical standards:\n1. **Preparation:** Ensure the patient has rested for at least 3-5 minutes. They should be sitting comfortably with their arm supported at heart level.\n2. **Cuff Placement:** Place the correct-sized cuff on the bare upper arm, about 2-3 cm above the elbow crease (cubital fossa).\n3. **Palpation (Riva-Rocci):** Feel the radial pulse, inflate the cuff until the pulse disappears (to estimate systolic pressure), then inflate 30 mmHg higher.\n4. **Auscultation:** Place the stethoscope over the brachial artery. Deflate the cuff slowly (2-3 mmHg per second).\n5. **Reading:** The first tapping sound (Korotkoff I) is the **Systolic** value. The point where sounds completely disappear (Korotkoff V) is the **Diastolic** value."},
            {"q": "What are the 5 rights of medication safety?", "a": "The 5 Rights of medication administration (5-R-Regel) is a fundamental safety protocol designed to prevent medication errors. Before administering any drug, a nurse must verify:\n1. **Right Patient (Richtiger Patient):** Always check the patient's name and date of birth.\n2. **Right Medication (Richtiges Medikament):** Double-check the drug name against the prescription.\n3. **Right Dose (Richtige Dosierung):** Ensure the correct concentration and amount.\n4. **Right Route (Richtige Applikationsform):** Ensure it is given correctly (e.g., oral, IV, subcutaneous).\n5. **Right Time (Richtiger Zeitpunkt):** Administer at the correct interval or time of day.\n*(Note: Some modern guidelines use the 6-R rule, adding 'Right Documentation').*"},
        ],
        "sidebar_lang": "🌐 Language",
        "sidebar_about_title": "📖 About PflegeKompassAI",
        "sidebar_about": """
**PflegeKompassAI** helps nursing students in Germany quickly find answers about their training, clinical basics, and everyday nursing practice.

**Why was it built?**
Many international nursing students struggle with Germany's language barrier and complex training system. PflegeKompassAI bridges that gap — in both English and German, completely free.

**Topics:**
- 🏥 Training structure & application
- 🩺 Vital signs & clinical basics
- 💊 Medication administration (5 Rights)
- 🧼 Hygiene & infection control
- 📋 Nursing documentation
- 🚨 Emergency situations
        """,
        "sidebar_clear": "🗑️ Clear Chat",
        # footer
        "f_desc": "AI chatbot for nursing students in Germany — answers questions about Ausbildung, clinical basics and medication in both English and German.",
        "f_c1": "Tech Stack",
        "f_c2": "Topics Covered",
        "f_c3": "About the Project",
        "f_topics": ["Training structure & application", "Vital signs & clinical basics", "Hygiene & infection control", "Medication (5 Rights)", "Nursing documentation", "Emergency situations"],
        "f_about": ["Built for international nursing students", "Bridges language & knowledge gaps", "Free & openly accessible", "v1.0 — actively in development"],
        "f_copy": "© {year} PflegeKompassAI. All rights reserved.",
        "f_by": "Built by",
    },
}

# ── Session State ──────────────────────────────────────────────────────────────
if "messages"          not in st.session_state: st.session_state.messages = []
if "language"          not in st.session_state: st.session_state.language = "de"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    lang = st.session_state.language
    t    = TEXTS[lang]

    st.markdown(f"### {t['sidebar_lang']}")
    choice = st.radio("lang", ["🇩🇪 Deutsch", "🇬🇧 English"],
                      index=0 if lang == "de" else 1,
                      label_visibility="collapsed")
    new_lang = "de" if "Deutsch" in choice else "en"
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()

    st.divider()
    t2 = TEXTS[st.session_state.language]
    st.markdown(f"### {t2['sidebar_about_title']}")
    st.markdown(t2["sidebar_about"])
    st.divider()
    if st.button(t2["sidebar_clear"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()


# ── Sayfa başında dil/metin güncelle ──────────────────────────────────────────
lang = st.session_state.language
t    = TEXTS[lang]


# ────────────────────────────────────────────────────────────────────────────
# NAVBAR  (PC)  — Streamlit columns ile; CSS ile pill-styled
# ────────────────────────────────────────────────────────────────────────────
nav_brand, nav_space, nav_en_col, nav_de_col = st.columns([5, 2, 1, 1])

with nav_brand:
    # Bu gizli div sayesinde CSS `:has(.nav-marker)` bu satiri bulup navbar stili verebilecek
    st.markdown(
        f'<div class="nav-marker nm-brand">🩺 PflegeKompassAI'
        f'<span class="nm-brand-tag">— {t["tagline"]}</span></div>',
        unsafe_allow_html=True,
    )

with nav_en_col:
    if st.button("🇬🇧 EN", key="nav_en",
                 type="primary" if lang == "en" else "secondary",
                 use_container_width=True):
        st.session_state.language = "en"
        st.rerun()

with nav_de_col:
    if st.button("🇩🇪 DE", key="nav_de",
                 type="primary" if lang == "de" else "secondary",
                 use_container_width=True):
        st.session_state.language = "de"
        st.rerun()




# ── Chat Geçmişi ───────────────────────────────────────────────────────────────
chat_html = '<div class="chat-container">'

if not st.session_state.messages:
    chat_html += f'''<div class="empty-state">
<div class="empty-state-greeting">{t["empty_title"]}</div>
</div>'''
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'<div class="user-message"><div class="user-bubble">{msg["content"]}</div></div>'
        else:
            content = msg["content"].replace("\n", "<br>")
            chat_html += f'<div class="bot-message"><div class="bot-avatar">🩺</div><div class="bot-bubble">{content}</div></div>'

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)


# ── Hızlı Sorular ─────────────────────────────────────────────────────────────
st.markdown(
    f'<p style="font-size:0.8rem;color:#aaa;margin:0.6rem 0 0.2rem 0;">⚡ {t["quick_label"]}</p>',
    unsafe_allow_html=True,
)
cols = st.columns(2)
for i, item in enumerate(t["quick_questions"]):
    with cols[i % 2]:
        if st.button(item["q"], key=f"quick_{i}", use_container_width=True):
            # Oto-cevap (AI kapalı)
            st.session_state.messages.append({"role": "user", "content": item["q"]})
            st.session_state.messages.append({"role": "assistant", "content": f"{t['quick_answer_prefix']}{item['a']}"})
            st.rerun()


# ── Soru İşleme (AI) ───────────────────────────────────────────────────────────
def process_question(question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner(t["thinking"]):
        response = ask(question, language=lang)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# ── Kullanıcı Girişi ───────────────────────────────────────────────────────────
user_input = st.chat_input(t["placeholder"])
if user_input:
    process_question(user_input)


# ────────────────────────────────────────────────────────────────────────────
# FOOTER  (PC only — mobilde CSS ile gizli)
# ────────────────────────────────────────────────────────────────────────────
year   = datetime.date.today().year
f_copy = t["f_copy"].format(year=year)
f_by   = t["f_by"]
desc   = "AI assistant for nursing Ausbildung in Germany" if lang == "en" else "KI-Assistent f\u00fcr die Pflegeausbildung in Deutschland"

footer_html = (
'<div class="nm-footer">'
'<div class="nm-footer-left">'
'🩺 <strong>PflegeKompassAI</strong>'
f'<span class="nm-footer-sep"> | </span><span class="nm-footer-desc">{desc}</span>'
f'<span class="nm-footer-sep"> | </span><span class="nm-footer-copy">{f_copy}</span>'
'</div>'
f'<div class="nm-footer-right">{f_by}<br><strong>Mustafa \u015eeno\u011flu</strong> <span class="nm-footer-heart">\u2665</span> <strong>M\u00fcsl\u00fcm Evin</strong></div>'
'</div>'
)

st.markdown(footer_html, unsafe_allow_html=True)


