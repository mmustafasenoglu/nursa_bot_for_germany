# 🩺 NurseMate AI — Nursing Ausbildung Assistant

An AI-powered chatbot for nursing students starting their **Pflegeausbildung** in Germany.
Built with a **Retrieval-Augmented Generation (RAG)** architecture to provide accurate,
hallucination-free answers based on official nursing guidelines.

> Developed over a dedicated 5-month learning period to demonstrate practical skills
> in AI/LLM integration and modern software development.

---

## 🚀 Live Demo

- **Frontend:** [https://nurse-mate-ai.vercel.app](https://nurse-mate-ai.vercel.app)
- **Backend:** [https://nurse-chat-backend.onrender.com](https://nurse-chat-backend.onrender.com)

---

## 🛠️ Tech Stack

| Layer | Technology | Why? |
|---|---|---|
| **LLM** | Groq API (Llama 3.1 8B) | Ultra-low latency inference |
| **Orchestration** | LangChain + LCEL | RAG pipeline management |
| **Vector Store** | FAISS (local) | No cloud limits, instant search |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | Open-source, fast, accurate |
| **Backend** | Django 5 + DRF | REST API, scalable |
| **Frontend** | React 19 + Vite 8 | Modern, fast UI |
| **Deployment** | Render (backend) + Vercel (frontend) | Free hosting |

---

## 📂 How It Works (RAG Pipeline)

```
User Question
     ↓
[FAISS] searches 2,500+ chunks of nursing knowledge
     ↓
[LangChain] builds context-aware prompt
     ↓
[Groq / Llama 3.1] generates answer based ONLY on retrieved context
     ↓
React frontend displays answer (no hallucinations)
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
git clone https://github.com/yourusername/nurse_chat_bpt.git
cd nurse_chat_bpt
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

# Set up your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Build FAISS index
python ingest.py

# Run backend
python manage.py runserver
```

Backend runs at: **http://localhost:8000**

### 3. Frontend Setup
```bash
cd frontend
npm install

# Set API URL
echo "VITE_API_URL=http://127.0.0.1:8000/api" > .env

# Run frontend
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## ☁️ Deployment

### Backend (Render)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python ingest.py`
   - **Start Command:** `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`
5. Add environment variables:
   - `SECRET_KEY` (generate)
   - `DEBUG=False`
   - `RENDER=True`
   - `GROQ_API_KEY=your_key`
6. Deploy!

### Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com) → New Project
2. Connect GitHub repo
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework:** Vite
4. Add environment variable:
   - `VITE_API_URL=https://your-backend.onrender.com/api`
5. Deploy!

---

## 📁 Project Structure

```
nurse_chat_bpt/
├── backend/                 # Django REST API
│   ├── core/               # Django project settings
│   ├── api/                # API endpoints
│   ├── rag_pipeline.py     # RAG engine (LangChain + FAISS + Groq)
│   ├── ingest.py           # Document ingestion script
│   ├── data/               # Knowledge base (txt + pdf)
│   ├── faiss_index/        # Generated FAISS vectors
│   ├── requirements.txt
│   ├── build.sh            # Render build script
│   └── manage.py
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   ├── api.js          # API client
│   │   └── components/     # UI components
│   ├── package.json
│   ├── vercel.json
│   └── vite.config.js
├── render.yaml             # Render deployment config
├── .env                    # API keys (gitignored)
├── .gitignore
└── README.md
```

---

## 🔒 Security Notes

- The `.env` file is listed in `.gitignore` and will **never** be uploaded to GitHub
- FAISS index is generated during build — no external database required
- CORS is configured to allow only the frontend domain

---

## 👤 About

Built by **Mustafa Şenoğlu** and **Müslüm Evin** as a portfolio project demonstrating:
- RAG (Retrieval-Augmented Generation) architecture
- LLM integration (Groq / Llama 3.1)
- Vector database operations (FAISS)
- Full-stack development (Django + React)
- Cloud deployment (Render + Vercel)
