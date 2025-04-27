# Intelligent Manufacturing Document Assistant

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview
A Q&A system for engineers and technicians to query complex manufacturing documentation using natural language. Built with open-source tools and models, it leverages:
- Hugging Face datasets (SQuAD, MS MARCO, WikiHow technical, Kaggle manufacturing)
- Sentence-BERT for embeddings
- ChromaDB as a vector store
- Open-source LLMs (Llama-3-8B or Mistral-7B) via external API (Transformers)
- Streamlit frontend

## Features
- Ingest and search technical documents
- Fast, semantic search using vector embeddings
- Natural language Q&A interface
- Fully open-source, free to use

## Setup
### Prerequisites
- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)

### Installation
```bash
# Clone the repo
git clone https://github.com/akshay-sisodia/intelligent-manufacturing-doc-assistant.git
cd intelligent-manufacturing-doc-assistant

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
- Copy `.env.example` to `.env` and fill in required API keys and settings.

### Running
```bash
streamlit run frontend.py
```

## Usage
- Upload or ingest manufacturing documents
- Ask questions in plain English
- Get instant, context-aware answers

## Project Structure
- `main.py` — Application entry point
- `frontend.py` — Streamlit UI
- `embedding_service.py` — Embedding logic
- `retrieval_service.py` — Vector search logic
- `llm_client.py` — LLM API integration
- `pdf_ingest.py` — PDF/document ingestion
- `config.py` — Configuration
- `data/` — Document datasets
- `chroma_db/` — Vector DB files
- `test_main.py` — Tests

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Maintainer
[akshay-sisodia](https://github.com/akshay-sisodia)
