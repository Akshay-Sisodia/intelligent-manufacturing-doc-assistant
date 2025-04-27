# Intelligent Manufacturing Document Assistant

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Open Source](https://img.shields.io/badge/open--source-yes-brightgreen)

---

## Overview
A Q&A system for engineers and technicians to query complex manufacturing documentation using natural language. Built with open-source tools and models, it leverages:
- Hugging Face datasets (SQuAD, MS MARCO, WikiHow technical, Kaggle manufacturing)
- Sentence-BERT for embeddings
- ChromaDB as a vector store
- Open-source LLMs (Llama-3-8B or Mistral-7B) via external API (Transformers)
- Streamlit frontend

---

## Project Architecture
```
[User/Engineer]
     |
[Streamlit Frontend] <----> [FastAPI Backend]
     |                             |
     |                   [Retriever, Embedder, LLM Client]
     |                             |
[ChromaDB Vector Store]   [External LLM API]
     |
[Manufacturing Docs (SQuAD, MS MARCO, WikiHow, Kaggle)]
```

---

## Quickstart
```bash
# 1. Clone the repo
git clone https://github.com/akshay-sisodia/intelligent-manufacturing-doc-assistant.git
cd intelligent-manufacturing-doc-assistant

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit environment variables
cp .env.example .env
# Edit .env with your API keys and config

# 5. Start the app
streamlit run frontend.py
```

---

## Configuration
All configuration is via environment variables (see `.env.example`).

| Variable             | Description                                 |
|---------------------|---------------------------------------------|
| DOCS_RAW_DIR        | Directory for raw PDF/tech docs              |
| DOCS_PROCESSED_DIR  | Directory for processed docs                 |
| CHROMA_DB_PATH      | Path for ChromaDB vector store               |
| REDIS_URL           | Redis cache URL                              |
| EMBEDDING_MODEL     | Sentence-BERT model name                     |
| GROQ_API_KEY        | API key for Groq LLM                         |
| GROQ_MODEL          | LLM model name (e.g., llama3-8b-8192)        |
| MISTRAL_API_KEY     | API key for Mistral OCR                      |
| SENTRY_DSN          | Sentry DSN for error tracking (optional)     |
| CORS_ORIGINS        | Allowed CORS origins                         |
| ADMIN_TOKEN         | Token for admin endpoints                    |

---

## Features
- Ingest and search technical documents
- Fast, semantic search using vector embeddings
- Natural language Q&A interface
- Upload, reindex, and manage docs from the UI
- Fully open-source, free to use

---

## Project Structure
- `main.py` — FastAPI backend
- `frontend.py` — Streamlit UI
- `embedding_service.py` — Embedding logic
- `retrieval_service.py` — Vector search logic
- `llm_client.py` — LLM API integration
- `pdf_ingest.py` — PDF/document ingestion
- `config.py` — Configuration
- `utils.py` — Utility functions
- `test_main.py` — Tests
- `data/` — Document datasets (not tracked)
- `chroma_db/` — Vector DB files (not tracked)

---

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. PRs, issues, and feature requests are welcome!

---

## Community & Support
- Maintainer: [akshay-sisodia](https://github.com/akshay-sisodia)
- Issues: [GitHub Issues](https://github.com/akshay-sisodia/intelligent-manufacturing-doc-assistant/issues)

---

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [ChromaDB](https://www.trychroma.com/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://groq.com/)
- [Mistral](https://mistral.ai/)

