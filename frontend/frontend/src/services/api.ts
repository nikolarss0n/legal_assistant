import axios from 'axios';
import config from '../config';

const API_URL = config.apiUrl;

export interface Article {
  number: string;
  title: string;
  content: string;
}

export interface LegalResponse {
  answer: string;
  articles: Article[];
}

export const searchLegalInfo = async (query: string): Promise<LegalResponse> => {
  try {
    const response = await axios.post(`${API_URL}/query`, { query });
    return response.data;
  } catch (error) {
    console.error('Error querying legal assistant:', error);
    // Return fallback response in case of error
    return {
      answer: 'Sorry, I could not process your request at this time. Please try again later.',
      articles: []
    };
  }
};

// No simulation - only real backend requests