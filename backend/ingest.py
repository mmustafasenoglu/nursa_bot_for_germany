"""
ingest.py — Belgeleri yükler, chunk'lar, FAISS index oluşturur.
Bu script sadece bir kez çalıştırılır (veya yeni belge eklenince).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

DATA_DIR = "./data"
FAISS_INDEX_PATH = "./faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents(data_dir: str):
    """data/ klasöründeki tüm .txt ve .pdf dosyalarını yükler."""
    txt_loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    pdf_loader = DirectoryLoader(
        data_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    
    documents = txt_loader.load()
    try:
        pdf_docs = pdf_loader.load()
        documents.extend(pdf_docs)
    except Exception as e:
        print(f"⚠️ PDF yükleme hatası: {e}")
        
    print(f"✅ {len(documents)} belge yüklendi.")
    return documents


def split_documents(documents):
    """Belgeleri küçük chunk'lara böler."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # Her chunk maksimum 800 karakter
        chunk_overlap=150,     # Chunk'lar arası 150 karakter örtüşme (bağlam kaybını önler)
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunk oluşturuldu.")
    return chunks


def create_faiss_index(chunks):
    """HuggingFace embedding modeli ile FAISS index oluşturur ve diske kaydeder."""
    print(f"🔄 Embedding modeli yükleniyor: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print("🔄 FAISS index oluşturuluyor...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"✅ FAISS index kaydedildi: {FAISS_INDEX_PATH}/")
    return vectorstore


if __name__ == "__main__":
    print("=" * 50)
    print("🩺 PflegeKompassAI — Belge Yükleme & Index Oluşturma")
    print("=" * 50)

    if not Path(DATA_DIR).exists():
        print(f"❌ Hata: '{DATA_DIR}' klasörü bulunamadı!")
        exit(1)

    documents = load_documents(DATA_DIR)
    if not documents:
        print("❌ Hata: Hiç belge bulunamadı!")
        exit(1)

    chunks = split_documents(documents)
    create_faiss_index(chunks)

    print("\n✅ Tüm işlemler tamamlandı!")
    print("   Şimdi: streamlit run app.py")
