import os
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import pipeline
from langchain_chroma import Chroma
from dotenv import load_dotenv
import structlog
import json

load_dotenv()
logger = structlog.get_logger()

# Utility to clean metadata for ChromaDB
ALLOWED_TYPES = (str, int, float, bool)
def clean_metadata(meta):
    clean = {}
    for k, v in meta.items():
        if isinstance(v, ALLOWED_TYPES):
            clean[k] = v
        elif isinstance(v, (list, dict)):
            try:
                clean[k] = json.dumps(v)
            except Exception:
                continue
        else:
            # Try to convert to string if possible
            try:
                clean[k] = str(v)
            except Exception:
                continue
    return clean

class Embedder:
    def __init__(self):
        model_name = os.environ["EMBEDDING_MODEL"]
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": "cpu"})
        self.chroma_db_path = os.environ["CHROMA_DB_PATH"]
        self.collection_name = "docs"
        self.chroma = Chroma(
            persist_directory=self.chroma_db_path,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )

    def embed_and_store(self, documents):
        texts = [doc['text'] for doc in documents]
        # Propagate all metadata fields except 'text', but clean for ChromaDB
        metadatas = [clean_metadata({k: v for k, v in doc.items() if k != 'text'}) for doc in documents]
        logger.info("Embedding sample metadata", sample=metadatas[:5])
        # Extra debug: check for missing doc_ids
        missing = [i for i, m in enumerate(metadatas) if m.get("doc_id") in (None, "", "MISSING_DOC_ID")]
        if missing:
            logger.warning("Some docs missing doc_id in metadata", indices=missing, samples=[metadatas[i] for i in missing])
        self.chroma.add_texts(texts, metadatas=metadatas)
        logger.info("Embeddings stored via LangChain", num=len(texts))

if __name__ == "__main__":
    chunks_path = os.path.join(os.environ["DOCS_PROCESSED_DIR"], "chunks.jsonl")
    with open(chunks_path, "r", encoding="utf-8") as f:
        documents = [json.loads(line) for line in f]
    embedder = Embedder()
    embedder.embed_and_store(documents)
