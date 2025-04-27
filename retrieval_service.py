import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import structlog

load_dotenv()
logger = structlog.get_logger()

class Retriever:
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
        self.retriever = self.chroma.as_retriever()

    def search(self, query: str, top_k: int = 5):
        return self.retriever.get_relevant_documents(query)[:top_k]

    def search_with_relevance_scores(self, query: str, top_k: int = 5, score_threshold: float = None):
        # Use Chroma's similarity_search_with_relevance_scores to get (doc, relevance_score) pairs in [0, 1]
        kwargs = {}
        if score_threshold is not None:
            kwargs['score_threshold'] = score_threshold
        docs_and_scores = self.chroma.similarity_search_with_relevance_scores(query, k=top_k, **kwargs)
        results = []
        for doc, score in docs_and_scores:
            source = doc.metadata.get("doc_id") or None
            results.append({
                "content": doc.page_content,
                "source": source,
                "score": score
            })
        return results
