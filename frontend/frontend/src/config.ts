const config = {
  // When using the development server, we use the relative URL
  apiUrl: import.meta.env.PROD 
    ? '/api'  // In production, use relative path to hit our express server
    : 'http://localhost:5001/api' // In development, hit the Flask backend directly
};

export default config;