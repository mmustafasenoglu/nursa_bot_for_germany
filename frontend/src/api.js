import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

let currentSessionId = `session_${Date.now()}`;

export const setSessionId = (id) => {
  currentSessionId = id;
};

export const getSessionId = () => currentSessionId;

export const askQuestion = async (question, language = 'de') => {
  try {
    const response = await api.post('/chat/', {
      question,
      language,
      session_id: currentSessionId,
    });
    return response.data.answer;
  } catch (error) {
    console.error("API Error:", error);
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error, { cause: error });
    }
    throw new Error('Connection failed. Please try again.', { cause: error });
  }
};

export const getChatHistory = async () => {
  try {
    const response = await api.get('/chat/history/', {
      params: { session_id: currentSessionId },
    });
    return response.data.history;
  } catch (error) {
    console.error("History fetch failed:", error);
    return [];
  }
};

export const clearChatHistory = async () => {
  try {
    await api.delete('/chat/history/', {
      params: { session_id: currentSessionId },
    });
    currentSessionId = `session_${Date.now()}`;
  } catch (error) {
    console.error("Clear history failed:", error);
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health/');
    return response.data;
  } catch (error) {
    console.error("Health check failed:", error);
    throw new Error('Health check failed', { cause: error });
  }
};
