import knowledge from './knowledge.json';

const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY;
const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const MODEL = 'llama-3.1-8b-instant';

// ── Chat History ──────────────────────────────────────────────
let chatHistory = [];

// ── Simple Keyword-Based Retrieval ───────────────────────────
function retrieveChunks(query, lang, topK = 5) {
  const queryLower = query.toLowerCase();
  const queryWords = queryLower
    .replace(/[^\w\säöüß]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);

  const scored = knowledge.chunks
    .filter(c => c.lang === lang)
    .map(chunk => {
      const textLower = chunk.text.toLowerCase();
      let score = 0;
      for (const word of queryWords) {
        const regex = new RegExp(word, 'gi');
        const matches = textLower.match(regex);
        if (matches) score += matches.length;
      }
      return { ...chunk, score };
    })
    .filter(c => c.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  if (scored.length === 0) {
    return knowledge.chunks
      .filter(c => c.lang === lang)
      .slice(0, topK);
  }

  return scored;
}

function formatContext(chunks) {
  return chunks.map((c, i) => `[${i + 1}] ${c.text}`).join('\n\n');
}

// ── System Prompts ───────────────────────────────────────────
const SYSTEM_PROMPT_DE = `Du bist NurseMate AI, ein erfahrener KI-Assistent speziell für Pflegeauszubildende in Deutschland.

DEINE ROLLE:
- Du hilfst Auszubildenden bei Fragen zur generalistischen Pflegeausbildung
- Du bist freundlich, professionell und pädagogisch einfühlsam
- Du verwendest klare, verständliche Sprache

REGELN:
1. Antworte NUR basierend auf dem untenstehenden Kontext
2. Strukturiere deine Antworten klar: verwende Aufzählungen oder Absätze
3. Wenn die Antwort NICHT im Kontext steht, sage ehrlich: "Diese Information habe ich leider nicht in meiner Wissensbasis."
4. Sei immer unterstützend und ermutigend
5. Bei kritischen Fragen (z.B. Notfälle) weise auf professionelle Hilfe hin

KONTEXT:
{context}

FRAGE: {question}

ANTWORT (auf Deutsch):`;

const SYSTEM_PROMPT_EN = `You are NurseMate AI, an experienced AI assistant for nursing students (Auszubildende) in Germany.

YOUR ROLE:
- You help students with questions about German generalist nursing training
- You are friendly, professional, and pedagogically sensitive
- You use clear, understandable language

RULES:
1. Answer ONLY based on the context provided below
2. Structure your answers clearly: use bullet points or paragraphs
3. If the answer is NOT in the context, say honestly: "I don't have that specific information in my knowledge base."
4. Always be supportive and encouraging
5. For critical questions (e.g., emergencies), advise seeking professional help

CONTEXT:
{context}

QUESTION: {question}

ANSWER (in English):`;

// ── Cache ────────────────────────────────────────────────────
const cache = {};

function getCacheKey(question, lang) {
  const raw = `${lang}:${question.trim().toLowerCase()}`;
  let hash = 0;
  for (let i = 0; i < raw.length; i++) {
    const chr = raw.charCodeAt(i);
    hash = ((hash << 5) - hash) + chr;
    hash |= 0;
  }
  return hash.toString(36);
}

// ── Main Ask Function ────────────────────────────────────────
export async function askQuestion(question, language = 'de') {
  const cacheKey = getCacheKey(question, language);
  if (cache[cacheKey]) return cache[cacheKey];

  if (!GROQ_API_KEY) {
    throw new Error('VITE_GROQ_API_KEY is not set');
  }

  const chunks = retrieveChunks(question, language, 5);
  const context = formatContext(chunks);

  const promptTemplate = language === 'de' ? SYSTEM_PROMPT_DE : SYSTEM_PROMPT_EN;
  const systemPrompt = promptTemplate
    .replace('{context}', context)
    .replace('{question}', question);

  const messages = [
    ...chatHistory.slice(-6),
    { role: 'user', content: systemPrompt }
  ];

  try {
    const response = await fetch(GROQ_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: MODEL,
        messages,
        temperature: 0.3,
        max_tokens: 1024
      })
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Groq API error: ${err}`);
    }

    const data = await response.json();
    const answer = data.choices[0].message.content;

    chatHistory.push({ role: 'user', content: question });
    chatHistory.push({ role: 'assistant', content: answer });
    if (chatHistory.length > 12) chatHistory = chatHistory.slice(-12);

    cache[cacheKey] = answer;
    return answer;
  } catch (error) {
    console.error('Ask error:', error);
    throw error;
  }
}

export function clearChatHistory() {
  chatHistory = [];
}

export function getChatHistory() {
  const history = [];
  for (let i = 0; i < chatHistory.length; i += 2) {
    if (chatHistory[i + 1]) {
      history.push({
        user: chatHistory[i].content,
        bot: chatHistory[i + 1].content
      });
    }
  }
  return history;
}
