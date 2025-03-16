# Bulgarian Labor Law Assistant - Frontend

A modern React frontend for the Bulgarian Labor Law Assistant. This application features an Apple Vision Pro-inspired glassy design with beautiful animations and a responsive layout.

![Bulgarian Labor Law Assistant UI](https://i.imgur.com/placeholder.png) 
*Placeholder: Screenshot will be added after first deployment*

## Features

- 🔍 Search and query Bulgarian labor law content
- 💎 Modern, glassy UI inspired by Apple Vision Pro
- ✨ Beautifully animated components with Framer Motion
- 📱 Responsive design that works on all devices
- 🧩 Elegant input and response cards
- 🔄 Simulated API integration (ready to connect to the Python backend)

## Tech Stack

- React 18 + TypeScript
- Vite for fast development
- Emotion for styled components
- Framer Motion for animations
- Axios for API calls

## Getting Started

### Prerequisites

- Node.js v16+
- npm or yarn

### Installation

1. Clone the repository
2. Install the dependencies:

```bash
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

This will start the application on http://localhost:5173.

### Production Build

To create a production build:

```bash
npm run build
```

The build files will be located in the `dist` directory.

### Running with Express Server

The project includes an Express server that can serve the built frontend and proxy API requests to the backend:

```bash
# First build the project
npm run build

# Then start the Express server
npm start
```

This will serve the application on http://localhost:3000 and proxy API requests to the Python backend.

## Backend Integration

The frontend communicates with the Bulgarian Labor Law Assistant backend that uses locally downloaded Gemma 3 model:

- In development mode, it connects directly to the Python backend at `http://localhost:5000/api`
- In production mode (Express server), it uses a proxy at `/api` that forwards requests to the backend

To run the backend:
1. Follow the instructions in `GEMMA_INTEGRATION.md` to set up the Gemma 3 model
2. Install required Python packages: `pip install transformers torch flask flask-cors`
3. Run the backend server: `python app.py`
4. The server will start at `http://localhost:5000`

Advanced configuration:
- You can modify the API URL in `src/config.ts` if your backend runs on a different port
- When running with the Express server, you can set the backend URL with an environment variable: `BACKEND_URL=http://your-backend-url npm start`

## Design Details

- Glassy cards with subtle animations and backdrop filters
- Animated background elements using blur effects
- Responsive layout with proper spacing
- Custom scrollbar styling
- Loading indicators for better UX
- Bilingual support (Bulgarian and English)

## Key Features

- **Bilingual Support**: The UI detects and responds in both Bulgarian and English
- **Multiple Legal Topics**: Supports queries about probation periods, leave, salary, and termination
- **Gemma 3 Integration**: Now using Google's Gemma 3 LLM with local model download (see GEMMA_INTEGRATION.md)
- **Responsive Design**: Works well on desktop and mobile devices
- **Apple Vision Pro Inspired**: Modern glassy UI with blur effects and animations

## License

MIT
