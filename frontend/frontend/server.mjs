import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5001';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));

// API proxy
app.post('/api/query', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/query`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error('Error proxying request to backend:', error);
    res.status(500).json({
      answer: 'Error connecting to the backend service. Please try again later.',
      articles: []
    });
  }
});

// Serve the React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`API requests will be proxied to ${BACKEND_URL}`);
  console.log(`Open http://localhost:${port} in your browser`);
});