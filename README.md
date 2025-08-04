# Buddhism Chatbot

A comprehensive RAG (Retrieval-Augmented Generation) chatbot system focused on Buddhism, built with Vietnamese Buddhist texts from classical Buddhist literatures. This project implements a full-stack solution for answering questions about Buddhist teachings using modern AI techniques.

## 🌐 Live Demo

**Try the chatbot here: [https://buddhism-chatbot.nguyenvanloc.com/](https://buddhism-chatbot.nguyenvanloc.com/)**

## 🎯 Project Overview

This project implements a complete RAG pipeline for Buddhist question-answering, featuring:

- **Document Processing**: XML to JSONL conversion with NER (Named Entity Recognition)
- **Semantic Search**: Vector embeddings using multilingual models
- **AI-Powered Responses**: LLM integration for contextual answers
- **Modern Web Interface**: React-based frontend with real-time chat
- **Production Deployment**: Dockerized microservices architecture

## 🏗️ Architecture

### Backend Components
- **FastAPI Backend** (`backend/`): RESTful API with `/ask` and `/health` endpoints
- **RAG Pipeline** (`backend/rag.py`): Retrieval-Augmented Generation implementation
- **LLM Integration** (`backend/llm/`): Support for multiple LLM providers (OpenAI, Azure, local models)
- **Vector Database**: Qdrant for semantic search and document retrieval

### Frontend
- **Next.js Application** (`frontend/`): Modern React-based chat interface
- **Real-time Chat**: Interactive conversation with citation support
- **Responsive Design**: Optimized for desktop and mobile devices

### Data Pipeline
- **Document Processing** (`docling/`): PDF to Markdown conversion
- **XML Processing**: Structured text extraction with NER annotations
- **Embedding Generation** (`embedding/`): Vector embeddings using `intfloat/multilingual-e5-base`
- **Data Upload** (`qdrant-client/`): Batch upload to vector database

## 📚 Data Sources

The chatbot is trained on classical Vietnamese Buddhist texts including:
- **An Sĩ Toàn Thư** (Complete Works of An Sĩ): Various volumes covering Buddhist ethics and practices
- **Kinh Tương Ưng Bộ**: Samyutta Nikaya (Connected Discourses)
- **Quan Âm Thị Kinh**: Avalokitesvara Sutra commentaries
- **Thiền Uyển Tập Anh**: Collection of Zen teachings

## 🛠️ Technology Stack

### Backend
- **Python 3.12+** with FastAPI
- **Qdrant** vector database
- **Sentence Transformers** for embeddings
- **LangChain/Custom LLM** integration
- **Docker** containerization

### Frontend
- **Next.js 14** with TypeScript
- **Tailwind CSS** for styling
- **React Hook Form** for chat interface

### DevOps & Deployment
- **Docker Compose** for local development
- **Production deployment** with reverse proxy
- **Health checks** and monitoring
- **Environment-based configuration**

## 🚀 Features Implemented

### ✅ Core RAG Pipeline
- [x] XML to JSONL conversion with metadata preservation
- [x] Multilingual embedding generation
- [x] Vector similarity search
- [x] Context-aware response generation
- [x] Citation and source tracking

### ✅ Backend API
- [x] FastAPI with async support
- [x] Health monitoring endpoints
- [x] Error handling and logging
- [x] Environment configuration
- [x] Docker deployment

### ✅ Frontend Interface
- [x] Modern chat interface
- [x] Real-time message streaming
- [x] Source citation display
- [x] Responsive design
- [x] Error handling

### ✅ Data Processing
- [x] PDF to Markdown conversion using Docling
- [x] NER entity extraction and annotation
- [x] Batch embedding generation
- [x] Qdrant collection management

### ✅ Deployment & Production
- [x] Docker containerization
- [x] Production deployment pipeline
- [x] Domain configuration and SSL
- [x] Health checks and monitoring

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Qdrant instance (local or cloud)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/hcmus-project-collection/eastern-religion-chatbot.git
cd eastern-religion-chatbot
```

2. **Environment Configuration**
```bash
cp .env.template .env
# Edit .env with your configuration
```

3. **Generate Embeddings** (Required)
```bash
# This step is required as embedding files are too large for GitHub
cd embedding
python embedding.py
```

4. **Start with Docker Compose**
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose up
```

5. **Upload Data to Qdrant**
```bash
cd qdrant-client
python upload_data_to_qdrant.py
```

### Manual Setup (Alternative)

1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Evaluation & Testing

The project includes comprehensive evaluation tools:
- **Automated Testing** (`evaluation/automated_testing/`): Backend API testing
- **Answer Quality Evaluation** (`evaluation/evaluate_answer/`): Response quality metrics
- **Similarity Testing** (`evaluation/similarity/`): Embedding similarity analysis
- **Test Datasets** (`evaluation/test_dataset/`): Curated Q&A pairs for validation

## 🔧 Configuration

Key configuration options in `.env`:
- `QDRANT_URL`: Vector database connection
- `QDRANT_COLLECTION_NAME`: Collection name (default: `buddhism_religion`)
- `EMBEDDING_MODEL_NAME`: Embedding model (default: `intfloat/multilingual-e5-base`)
- `OPENAI_API_KEY`: LLM API configuration
- `PORT`: Backend server port

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
├── frontend/               # Next.js frontend
├── embedding/              # Embedding generation
├── qdrant-client/          # Vector DB client
├── docling/               # Document processing
├── evaluation/            # Testing & evaluation
├── xml/                   # Processed XML data
├── jsonl/                 # JSONL datasets
└── docs/                  # Documentation
```

## 🤝 Contributing

This project follows the development stages outlined in `docs/TODO.md`. Contributions are welcome for:
- Additional Buddhist text sources
- Improved NER and entity extraction
- Enhanced evaluation metrics
- UI/UX improvements
- Performance optimizations

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

---

## Motivation

This is done as a final project for the "Advanced Natural Language Processing" subject (MTH020), for the Master's program at the University of Science, VNUHCM.
