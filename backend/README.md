# QuestGen AI - Backend

Flask backend for AI-based automated exam question paper generation and CO-PO mapping system.

## Technologies

- **Flask**: Web framework
- **Google Gemini API**: LLM for question generation
- **RAG (Retrieval Augmented Generation)**: Document processing and context retrieval
- **PyPDF2 & pdfplumber**: PDF text extraction
- **Sentence Transformers** (Optional): Text embeddings for semantic search - falls back to simple text matching if not available

## Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** The basic requirements will install without issues. If you want advanced semantic search capabilities, you can optionally install sentence-transformers separately (it requires additional dependencies like PyTorch):
```bash
pip install sentence-transformers
```
However, the system will work fine without it using simple text-based retrieval.

### Configuration

The Gemini API key is already configured in `app.py`. If you need to change it, modify the `GEMINI_API_KEY` variable.

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if server is running

### File Upload
- `POST /api/upload/previous-papers` - Upload 1-3 previous question papers
- `POST /api/upload/copo` - Upload CO/PO mapping file
- `POST /api/upload/syllabus` - Upload course syllabus

### Processing
- `POST /api/process/read-pdfs` - Read and process all uploaded PDFs using AI
- `POST /api/generate/questions` - Generate questions using RAG and Gemini

## File Structure

```
backend/
├── app.py              # Main Flask application
├── pdf_processor.py    # PDF reading and text extraction
├── rag_system.py       # RAG system for document processing
├── requirements.txt    # Python dependencies
├── uploads/           # Uploaded files (created automatically)
└── README.md          # This file
```

## Features

- PDF text extraction using multiple methods (pdfplumber and PyPDF2)
- RAG system for intelligent document retrieval
- Gemini API integration for question generation
- Semantic search using sentence transformers
- Document chunking and embedding generation

