# Elara AI 

An AI-powered chatbot backend built with FastAPI, powered by Retrieval-Augmented Generation (RAG) with document processing, Supabase database integration, and Docker containerization.  Provides chat APIs, document upload and management, and serves a frontend via FastAPI.

![Home Page Screenshot](https://raw.githubusercontent.com/VathareVinayak/Elara/main/frontend/assets/home.png)

---

## Features

- Real-time WebSocket chat with RAG integration for context-aware answers  
- Document upload, chunking, embedding, and vector search  
- Supabase backend for relational and vector data storage  
- FastAPI backend with REST and WebSocket APIs  
- Frontend served via FastAPI for chat and admin web pages  
- Fully containerized with Docker for portability  

---

## Project Structure

```
Elara/
├── backend/                 # Backend FastAPI app code
│   ├── app/
│   ├── main.py              # FastAPI app initialization
├── frontend/                # Static frontend assets
├── documentation/           # Optional project docs
├── scripts/                 # Utility scripts
├── tests/                   # Test cases (if any)
├── uploaded_files/          # Uploaded documents store
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker instructions
├── .env                     # Environment variables (excluded from repo)
├── README.md                # Project documentation
```

---

## Setup and Running Locally

### Prerequisites

- Python 3.10.11+  
- Docker installed (optional, for containerization)  
- Supabase account with appropriate APIs and keys 
- HUGGINGFACE_HUB_TOKEN of  `Sentence-Transformer `  
- OPENROUTER_API_KEY ( `anthropic/claude-3-haiku `)

### Clone the repo and set environment

Create a `.env` file in your project directory with:

```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENROUTER_API_KEY=your_openrouter_api_key
HUGGINGFACE_HUB_TOKEN=your_huggingface_token
```

### Install dependencies (optional without Docker)

```
pip install -r requirements.txt
```

### Running the app locally (optional)

```
uvicorn backend.app.main:app --reload
```

Access the frontend at:

```
http://127.0.0.1:8000
```

---

## Docker Usage

### Build Docker image

```
docker build -t elara .
```

### Run Docker container

```
docker run --env-file .env -p 8000:8000 elara
```

Access the app via:

```
http://127.0.0.1:8000
```

---

## API Endpoints

| Method | Endpoint        | Description                        |
|--------|-----------------|----------------------------------|
| GET    | `/`             | Serve frontend home page          |
| GET    | `/chat`         | Serve chat frontend and APIs     |
| GET    | `/admin`        | Admin dashboard                  |
| POST   | `/documents`    | Upload documents                 |


Refer to source code and documentation for detailed API specs.

---

## Contact

For questions or contributions, contact:

- Name: Vinayak Vathare
- Email: vinayak.vathare2004@gmail.com  
- GitHub: [VathareVinayak](https://github.com/VathareVinayak)
