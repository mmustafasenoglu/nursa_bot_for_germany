# 🩺 NurseMate AI — Nursing Ausbildung Assistant

An AI-powered chatbot for nursing students starting their **Pflegeausbildung** in Germany.
Built with a **Retrieval-Augmented Generation (RAG)** architecture to provide accurate,
hallucination-free answers based on official nursing guidelines.

> Developed over a dedicated 5-month learning period to demonstrate practical skills
> in AI/LLM integration and modern software development.

---

## 🚀 Live Demo

👉 **[Open NurseMate AI](https://your-app-name.streamlit.app)** *(replace after deploying)*

---

## 🛠️ Tech Stack

| Layer | Technology | Why? |
|---|---|---|
| **LLM** | Groq API (Llama 3 8B) | Ultra-low latency inference |
| **Orchestration** | LangChain | RAG pipeline management |
| **Vector Store** | FAISS (local) | No cloud limits, instant search |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | Open-source, fast, accurate |
| **Frontend** | Streamlit | Clean chat UI, fast deployment |
| **Language** | Python 3.11+ | |

---

## 📂 How It Works (RAG Pipeline)

```
User Question
     ↓
[FAISS] searches 2,500+ chunks of nursing knowledge
     ↓
[LangChain] builds context-aware prompt
     ↓
[Groq / Llama 3] generates answer based ONLY on retrieved context
     ↓
Streamlit displays answer (no hallucinations)
```

---

## 📚 Knowledge Base Topics

- ✅ Ausbildung structure, duration, and application process
- ✅ Language requirements (B2/C1 German)
- ✅ Salary during and after training
- ✅ Vital signs measurement (blood pressure, pulse, SpO₂, temperature)
- ✅ Hygiene and infection control (WHO 5 Moments)
- ✅ Basic nursing care (Grundpflege)
- ✅ Medication safety (5-R-Regel / 5 Rights)
- ✅ Nursing documentation principles
- ✅ Emergency recognition (CPR, stroke FAST, hypoglycaemia)
- ✅ Recognition of foreign qualifications (Anerkennung)
- ✅ Patient rights and medical ethics

---

## 🛠️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/nursing-ausbildung-bot.git
cd nursing-ausbildung-bot
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your Groq API key
Get your free API key at [console.groq.com](https://console.groq.com)

```bash
# Edit .env file:
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Build the FAISS index (run once)
```bash
python ingest.py
```

### 6. Launch the app
```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub *(make sure `.env` is in `.gitignore`)*
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your secret: **Settings → Secrets** → add `GROQ_API_KEY = "your_key"`
5. Deploy! 🎉

---

## 📁 Project Structure

```
nurse_chat_bpt/
├── app.py              # Streamlit UI
├── rag_pipeline.py     # RAG engine (LangChain + FAISS + Groq)
├── ingest.py           # One-time document ingestion script
├── data/
│   ├── ausbildung_guide_de.txt   # German Ausbildung guide
│   ├── ausbildung_guide_en.txt   # English Ausbildung guide
│   ├── nursing_basics_de.txt     # German clinical knowledge
│   └── nursing_basics_en.txt     # English clinical knowledge
├── faiss_index/        # Auto-generated FAISS vectors (gitignored)
├── requirements.txt
├── .env                # API keys (gitignored — never commit!)
├── .gitignore
└── README.md
```

---

## 🔒 Security Notes

- The `.env` file is listed in `.gitignore` and will **never** be uploaded to GitHub
- When deploying to Streamlit Cloud, add your API key via the **Secrets** panel, not in code
- FAISS index is stored locally — no external database required

---

## 👤 About

Built by **Mustafa Şenoğlu** as a portfolio project demonstrating:
- RAG (Retrieval-Augmented Generation) architecture
- LLM integration (Groq / Llama 3)
- Vector database operations (FAISS)
- End-to-end ML product deployment

📧 Contact: [your-email@example.com]
🔗 LinkedIn: [your-linkedin-url]
