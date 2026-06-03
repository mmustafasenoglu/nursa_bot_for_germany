"""
rag_pipeline.py — RAG motoru.
FAISS index'ini yükler, Groq LLM'e bağlanır, soru-cevap zinciri kurar.
"""

import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

FAISS_INDEX_PATH = "./faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── Sistem Promptları ──────────────────────────────────────────────────────────

SYSTEM_PROMPT_DE = """Du bist NurseMate, ein hilfreicher KI-Assistent für Pflegeauszubildende in Deutschland.
Du hilfst Auszubildenden beim Einstieg in die generalistische Pflegeausbildung und beantwortest ihre Fragen freundlich und kompetent.

Nutze die folgenden Kontextinformationen, um die Frage zu beantworten. 
Wenn du die Antwort im Kontext findest, nutze sie.
Wenn die Antwort nicht im Kontext steht, nutze dein allgemeines Wissen über die deutsche Pflegeausbildung und Medizin, um so gut wie möglich zu helfen, anstatt die Antwort zu verweigern. Sei immer unterstützend und informativ.

Kontext:
{context}

Frage: {question}

Antwort (auf Deutsch, klar und hilfreich für Auszubildende):"""

SYSTEM_PROMPT_EN = """You are NurseMate, a helpful AI assistant for nursing students in Germany. 
You help beginners navigate the German nursing training program (Ausbildung) and answer their questions in a friendly and competent manner.

Use the following context information to answer the question.
If you find the answer in the context, use it.
If the answer is not in the context, use your general knowledge about German nursing training and medicine to help as much as possible, instead of refusing to answer. Always be supportive and informative.

Context:
{context}

Question: {question}

Answer (in English, clear and helpful for nursing students):"""

# ── Embedding Loader ───────────────────────────────────────────────────────────

_embeddings = None


def get_embeddings():
    """Singleton — embedding modelini bir kez yükler."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


# ── FAISS Loader ───────────────────────────────────────────────────────────────

_vectorstore = None


def get_vectorstore():
    """FAISS index'ini yükler (singleton)."""
    global _vectorstore
    if _vectorstore is None:
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index bulunamadı: '{FAISS_INDEX_PATH}'\n"
                "Lütfen önce şunu çalıştırın: python ingest.py"
            )
        _vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    return _vectorstore


# ── LLM ───────────────────────────────────────────────────────────────────────

def get_llm():
    """Groq LLM oluşturur. Streamlit Cloud secrets veya .env'den key alır."""
    # Önce Streamlit secrets dene (Cloud deployment için)
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    # Yoksa .env'den al (local geliştirme için)
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY bulunamadı!\n"
            "Local: .env dosyasına GROQ_API_KEY=... ekleyin\n"
            "Cloud: Streamlit dashboard > Secrets bölümüne ekleyin"
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=1024,
        groq_api_key=api_key,
    )


# ── RAG Chain ─────────────────────────────────────────────────────────────────

def build_rag_chain(language: str = "en"):
    """LCEL RAG zinciri oluşturur (LangChain 0.3.x)."""
    prompt_template = SYSTEM_PROMPT_DE if language == "de" else SYSTEM_PROMPT_EN

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain


# ── Ana Soru-Cevap Fonksiyonu ─────────────────────────────────────────────────


FALLBACK_ANSWERS = {
    # English
    "How long does the nursing Ausbildung take?": "The nursing Ausbildung typically takes 3 years (36 months) of full-time training, combining theoretical instruction at a nursing school with practical training in clinical settings.",
    "What German language level do I need?": "You generally need at least a B2 level of German to start the nursing Ausbildung, as strong communication skills are required for patient care and studying.",
    "How much do I earn during training?": "Trainees earn a monthly salary which increases each year. Typically, it starts around €1,100 to €1,300 gross in the first year and goes up to €1,300 to €1,500 gross in the third year.",
    "What are the duties of a nurse?": "Nurses perform basic and treatment care, monitor vital signs, administer medication, document patient progress, and provide emotional support to patients and families.",
    "How does the nursing exam work?": "The final exam consists of three parts: a written exam (theoretical knowledge), an oral exam, and a practical exam (demonstrating nursing skills on real patients).",
    "What is Anerkennung (recognition of foreign diplomas)?": "Anerkennung is the official process of evaluating your foreign nursing qualifications to see if they match the German standards, often requiring adaptation courses or exams.",
    "How do I measure blood pressure correctly?": "Ensure the patient rests for 5 minutes. Place the cuff on the upper arm at heart level, inflate it, and slowly release the pressure while listening for the systolic and diastolic sounds, or use an automatic machine.",
    "What are the 5 rights of medication safety?": "The 5 Rights are: 1. Right Patient, 2. Right Medication, 3. Right Dose, 4. Right Route (e.g., oral, IV), and 5. Right Time.",
    # German
    "Wie lange dauert die Pflegeausbildung?": "Die generalistische Pflegeausbildung dauert in der Regel 3 Jahre (36 Monate) in Vollzeit und besteht aus Theorieprüfungen in der Pflegeschule sowie Praxiseinsätzen in Krankenhäusern oder Pflegeheimen.",
    "Welches Sprachniveau brauche ich?": "In der Regel wird mindestens das Sprachniveau B2 vorausgesetzt. Starke Deutschkenntnisse sind für die Arbeit am Patienten und den Schulunterricht zwingend erforderlich.",
    "Wie viel verdiene ich während der Ausbildung?": "Auszubildende erhalten eine Ausbildungsvergütung. Diese liegt im ersten Jahr meist bei ca. 1.100 bis 1.300 Euro brutto und steigt bis zum dritten Jahr auf ca. 1.300 bis 1.500 Euro brutto an.",
    "Was sind die Aufgaben einer Pflegefachkraft?": "Zu den Aufgaben gehören unter anderem Grund- und Behandlungspflege, Kontrolle der Vitalwerte, Medikamentengabe, Pflegedokumentation sowie die Beratung und Betreuung von Patienten und Angehörigen.",
    "Wie läuft die Abschlussprüfung ab?": "Die Prüfung ist staatlich anerkannt und gliedert sich in drei Teile: einen schriftlichen Teil, einen mündlichen Teil und einen praktischen Teil direkt am Patienten.",
    "Was bedeutet 'Anerkennung' (ausländischer Abschlüsse)?": "Die Anerkennung ist das offizielle Verfahren, bei dem geprüft wird, ob eine im Ausland erworbene Pflegequalifikation den deutschen Standards entspricht. Oft sind danach Anpassungslehrgänge oder Kenntnisprüfungen nötig.",
    "Wie messe ich den Blutdruck richtig?": "Lassen Sie den Patienten 5 Minuten ruhen. Legen Sie die Manschette am Oberarm auf Herzhöhe an, pumpen Sie sie auf und lassen Sie den Druck langsam ab, während Sie die systolischen und diastolischen Werte ermitteln (oder nutzen Sie ein automatisches Gerät).",
    "Was ist die 5-R-Regel bei der Medikamentengabe?": "Die 5-R-Regel lautet: 1. Richtiger Patient, 2. Richtiges Medikament, 3. Richtige Dosierung, 4. Richtige Applikationsform (z. B. oral, i.v.), und 5. Richtiger Zeitpunkt."
}

def ask(question: str, language: str = "en") -> str:
    """
    Kullanıcı sorusunu alır, RAG pipeline üzerinden cevap üretir.

    Args:
        question: Kullanıcının sorusu
        language: "en" (İngilizce) veya "de" (Almanca)

    Returns:
        LLM'in ürettiği cevap, AI çökerse varsayılan hazır cevap.
    """
    try:
        chain = build_rag_chain(language)
        return chain.invoke(question)
    except Exception as e:
        # Hata durumunda statik soruları kontrol et ve onlardan cevap dön
        fallback = FALLBACK_ANSWERS.get(question.strip())
        if fallback:
            return fallback
        
        # Eğer soru listede yoksa genel bir özür mesajı
        if language == "de":
            return "Entschuldigung, unsere Systeme sind derzeit stark ausgelastet. Bitte versuchen Sie es später noch einmal."
        else:
            return "Sorry, our systems are currently experiencing high load. Please try again later."
