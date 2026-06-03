import time
from rag_pipeline import ask

# Test edilecek temel senaryolar
TEST_CASES = [
    {"lang": "en", "q": "How long does the nursing Ausbildung take?"},
    {"lang": "de", "q": "Was sind die normalen Vitalwerte für den Blutdruck?"},
    {"lang": "en", "q": "What are the 5 rights of medication safety?"},
    {"lang": "de", "q": "Welches Sprachniveau brauche ich?"},
    {"lang": "en", "q": "What is the capital of France?"}  # Out of context test (to see how RAG handles hallucinations)
]

print("="*60)
print("🩺 NurseMate AI - RAG Pipeline Test Scripti")
print("="*60 + "\n")

for i, tc in enumerate(TEST_CASES, 1):
    lang = tc["lang"]
    query = tc["q"]
    print(f"[{i}/{len(TEST_CASES)}] ({lang.upper()}) Soru: {query}")
    
    start_time = time.time()
    try:
        # dotenv yüklemesi rag_pipeline içinde var varsayıyoruz
        answer = ask(query, language=lang)
        elapsed = time.time() - start_time
        print(f"✅ Yanıt ({elapsed:.2f}s):\n{answer}")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        
    print("-" * 60 + "\n")

print("✅ Bütün testler tamamlandı!")
