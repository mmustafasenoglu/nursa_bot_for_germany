import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const askQuestion = async (question, language = 'de') => {
  try {
    const response = await axios.post(`${API_URL}/chat/`, {
      question,
      language,
    });
    return response.data.answer;
  } catch (error) {
    console.error("Error connecting to API", error);
    throw error;
  }
};
