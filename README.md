# AI Fake News Detector 🔍

A production-ready web application for detecting fake news using a fine-tuned BERT model. Built with FastAPI (Python) and React, containerized with Docker.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18)                       │
│         Vite • Modern UI • Dark Theme • Responsive           │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  1. Receive text → 2. Preprocess → 3. BERT Inference         │
│  Returns: { prediction: "Fake|Real", confidence: 0.0-1.0 }   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   ML MODEL (BERT)                            │
│        Fine-tuned binary classifier (Fake=0, Real=1)         │
│        Loaded once at startup using HuggingFace              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
fake-news-detector/
├── model_training/              # Your trained model (existing)
│   └── saved_model/
│       └── fake-news-bert/      # BERT model files
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py              # API endpoints
│   │   ├── model.py             # Model loading & inference
│   │   ├── schemas.py           # Pydantic models
│   │   ├── utils.py             # Text preprocessing
│   │   └── config.py            # Configuration
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── TextInput.jsx    # Input component
│   │   │   └── ResultCard.jsx   # Result display
│   │   ├── App.jsx              # Main component
│   │   ├── api.js               # API client
│   │   └── index.css            # Styling
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml           # Container orchestration
└── README.md
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to the project
cd fake-news-detector

# Build and run all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Run Locally

#### Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
# Navigate to frontend directory (new terminal)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:5173
```

## 📡 API Reference

### Analyze Text

**POST** `/analyze`

Analyze news text for fake news detection.

**Request:**
```json
{
  "text": "Breaking news: Scientists discover revolutionary technology..."
}
```

**Response:**
```json
{
  "prediction": "Real",
  "confidence": 0.9247
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Scientists at MIT have developed a new solar panel technology that can generate electricity from thermal radiation at night."}'
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Model** | BERT (Hugging Face Transformers) |
| **Backend** | FastAPI, Python 3.10, PyTorch |
| **Frontend** | React 18, Vite, Axios |
| **Styling** | Vanilla CSS (Dark Theme) |
| **Container** | Docker, Docker Compose |
| **Server** | Uvicorn (ASGI), Nginx |

## 📋 Features

- ✅ **Real-time Analysis**: Instant fake news detection
- ✅ **Confidence Scoring**: Probability-based results (0-100%)
- ✅ **Modern UI**: Dark theme with responsive design
- ✅ **Error Handling**: Graceful error states
- ✅ **API Documentation**: Auto-generated Swagger UI
- ✅ **Docker Ready**: One-command deployment
- ✅ **Production Ready**: CORS, health checks, logging

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `../model_training/saved_model/fake-news-bert` | Path to saved model |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL (frontend) |

## 🧪 Testing

### Backend Syntax Check
```bash
cd backend
python -m py_compile app/main.py app/model.py app/schemas.py
```

### Frontend Build Test
```bash
cd frontend
npm run build
```

## 📝 Notes

- The model is loaded **once** at startup for optimal performance
- Input text is automatically cleaned (HTML, URLs, extra whitespace removed)
- Maximum input length is 10,000 characters (truncated for BERT's 512 token limit)
- GPU acceleration is automatically used if available

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ using FastAPI & React**
