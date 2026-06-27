"""
rag_pipeline.py — RAG motoru (v2 — geliştirilmiş).
FAISS index'ini yükler, Groq LLM'e bağlanır, soru-cevap zinciri kurar.
Chat history ve cache desteği eklenmiştir.
"""

import os
import hashlib
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── Sistem Promptları (v2 — yapılandırılmış) ─────────────────────────────────

SYSTEM_PROMPT_DE = """Du bist NurseMate AI, ein erfahrener KI-Assistent speziell für Pflegeauszubildende in Deutschland.

DEINE ROLLE:
- Du hilfst Auszubildenden bei Fragen zur generalistischen Pflegeausbildung
- Du bist freundlich, professionell und pädagogisch einfühlsam
- Du verwendest klare, verständliche Sprache (kein unnötiger Fachjargon)
- Du bist ein vertrauenswürdiger Begleiter für die Ausbildung

REGELN:
1. Antworte NUR basierend auf dem untenstehenden Kontext
2. Strukturiere deine Antworten klar: verwende Aufzählungen, Schritte oder Absätze
3. Wenn du die Antwort im Kontext findest, nutze sie direkt
4. Wenn die Antwort NICHT im Kontext steht, sage ehrlich: "Diese Information habe ich leider nicht in meiner Wissensbasis. Bitte wende dich an deine Pflegeschule oder deinen Ausbildungsbetrieb."
5. Sei immer unterstützend und ermutigend
6. Bei kritischen Fragen (z.B. Notfälle) weise immer darauf hin, professionelle Hilfe zu suchen

KONTEXT:
{context}

FRAGE: {question}

ANTWORT (auf Deutsch, klar strukturiert und hilfreich):"""

SYSTEM_PROMPT_EN = """You are NurseMate AI, an experienced AI assistant specifically designed for nursing students (Auszubildende) in Germany.

YOUR ROLE:
- You help students with questions about the German generalist nursing training (Ausbildung)
- You are friendly, professional, and pedagogically sensitive
- You use clear, understandable language (avoid unnecessary jargon)
- You are a trustworthy companion throughout the training

RULES:
1. Answer ONLY based on the context provided below
2. Structure your answers clearly: use bullet points, steps, or paragraphs
3. If you find the answer in the context, use it directly
4. If the answer is NOT in the context, honestly say: "I don't have that specific information in my knowledge base. Please consult your nursing school or training institution."
5. Always be supportive and encouraging
6. For critical questions (e.g., emergencies), always advise seeking professional help

CONTEXT:
{context}

QUESTION: {question}

ANSWER (in English, clearly structured and helpful):"""

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

_llm = None


def get_llm():
    """Groq LLM oluşturur (singleton). .env'den key alır."""
    global _llm
    if _llm is not None:
        return _llm

    api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY bulunamadı!\n"
            ".env dosyasına GROQ_API_KEY=... ekleyin"
        )

    _llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=1024,
        groq_api_key=api_key,
    )
    return _llm


# ── Cache ──────────────────────────────────────────────────────────────────────

_response_cache = {}


def _cache_key(question: str, language: str) -> str:
    """Cache key oluşturur."""
    raw = f"{language}:{question.strip().lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


# ── Retriever ─────────────────────────────────────────────────────────────────

_retriever = None


def get_retriever():
    """Retriever'ı singleton olarak döndürür."""
    global _retriever
    if _retriever is None:
        vectorstore = get_vectorstore()
        _retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5, "fetch_k": 8},
        )
    return _retriever


def format_docs(docs):
    """Retrieved doc'ları formatlar."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "bilinmeyen kaynak")
        formatted.append(f"[Kaynak {i}: {source}]\n{doc.page_content}")
    return "\n\n".join(formatted)


# ── RAG Chain ─────────────────────────────────────────────────────────────────

def build_rag_chain(language: str = "en"):
    """LCEL RAG zinciri oluşturur — chat history desteği ile."""
    prompt_template = SYSTEM_PROMPT_DE if language == "de" else SYSTEM_PROMPT_EN

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    def extract_question(x):
        if isinstance(x, dict):
            return x.get("question", str(x))
        return str(x)

    def extract_history(x):
        if isinstance(x, dict):
            return x.get("chat_history", [])
        return []

    retriever_chain = get_retriever()

    def retrieve_docs(x):
        q = extract_question(x)
        docs = retriever_chain.invoke(q)
        return format_docs(docs)

    chain = (
        {
            "context": RunnableLambda(retrieve_docs),
            "question": RunnableLambda(extract_question),
            "chat_history": RunnableLambda(extract_history),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    return chain


# ── Chat History Yönetimi ─────────────────────────────────────────────────────

class ConversationMemory:
    """Basit chat history yöneticisi."""

    def __init__(self, max_history: int = 6):
        self.max_history = max_history
        self.messages: list = []

    def add(self, human_msg: str, ai_msg: str):
        self.messages.append(HumanMessage(content=human_msg))
        self.messages.append(AIMessage(content=ai_msg))
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-(self.max_history * 2):]

    def get_history(self) -> list:
        return self.messages.copy()

    def clear(self):
        self.messages = []


_conversations: dict[str, ConversationMemory] = {}


def get_conversation(session_id: str = "default") -> ConversationMemory:
    """Session bazlı conversation memory döndürür."""
    if session_id not in _conversations:
        _conversations[session_id] = ConversationMemory()
    return _conversations[session_id]


def clear_conversation(session_id: str = "default"):
    """Belirli bir session'ı temizler."""
    if session_id in _conversations:
        _conversations[session_id].clear()


# ── Ana Soru-Cevap Fonksiyonu ─────────────────────────────────────────────────

FALLBACK_ANSWERS = {
    "How long does the nursing Ausbildung take?": "The nursing Ausbildung typically takes 3 years (36 months) of full-time training.",
    "What German language level do I need?": "You generally need at least a B2 level of German to start the nursing Ausbildung.",
    "How much do I earn during training?": "Trainees earn a monthly salary: ~€1,340 (1st year), ~€1,400 (2nd year), ~€1,500 (3rd year).",
    "What are the duties of a nurse?": "Nurses perform basic and treatment care, monitor vital signs, administer medication, and document patient progress.",
    "How does the nursing exam work?": "The final exam consists of three parts: written, oral, and practical.",
    "How do I measure blood pressure correctly?": "Patient rests 5 minutes. Cuff on upper arm at heart level. Inflate and slowly release while listening for Korotkoff sounds.",
    "What are the 5 rights of medication safety?": "1. Right Patient, 2. Right Medication, 3. Right Dose, 4. Right Route, 5. Right Time.",
    "Wie lange dauert die Pflegeausbildung?": "Die generalistische Pflegeausbildung dauert 3 Jahre in Vollzeit.",
    "Welches Sprachniveau brauche ich?": "Mindestens B2 wird vorausgesetzt.",
    "Was sind die Aufgaben einer Pflegefachkraft?": "Grund- und Behandlungspflege, Vitalwerte, Medikamentengabe, Dokumentation.",
    "Wie messe ich den Blutdruck richtig?": "Patient 5 Min ruhen lassen. Manschette am Oberarm, aufpumpen, langsam ablassen. Systolisch = erstes Geräusch, Diastolisch = Verschwinden.",
    "Was ist die 5-R-Regel bei der Medikamentengabe?": "1. Richtiger Patient, 2. Richtiges Medikament, 3. Richtige Dosierung, 4. Richtige Applikationsform, 5. Richtiger Zeitpunkt."
}


def ask(question: str, language: str = "en", session_id: str = "default") -> str:
    """
    Kullanıcı sorusunu alır, RAG pipeline üzerinden cevap üretir.
    Chat history ve cache desteği içerir.
    """
    key = _cache_key(question, language)
    if key in _response_cache:
        return _response_cache[key]

    try:
        conversation = get_conversation(session_id)
        chain = build_rag_chain(language)

        result = chain.invoke({
            "question": question,
            "chat_history": conversation.get_history(),
        })

        conversation.add(question, result)
        _response_cache[key] = result
        return result
    except Exception:
        fallback = FALLBACK_ANSWERS.get(question.strip())
        if fallback:
            return fallback
        if language == "de":
            return "Entschuldigung, unsere Systeme sind derzeit stark ausgelastet. Bitte versuchen Sie es später noch einmal."
        else:
            return "Sorry, our systems are currently experiencing high load. Please try again later."
