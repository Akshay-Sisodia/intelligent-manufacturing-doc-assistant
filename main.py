import os
import time
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import structlog
import sentry_sdk
from starlette.responses import Response
from dotenv import load_dotenv
import redis
import shutil
import json
import threading
import logging
from embedding_service import Embedder
from retrieval_service import Retriever
from llm_client import LLMClient
from pdf_ingest import ingest_pdfs
from langchain.chains import RetrievalQA

load_dotenv()
logger = structlog.get_logger()

# Set logging to INFO to reduce debug output
logging.basicConfig(level=logging.INFO)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))

os.makedirs(os.environ["DOCS_RAW_DIR"], exist_ok=True)
sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN", ""))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])

embedder = Embedder()
retriever = Retriever()
llm_client = LLMClient()

def build_qa_chain():
    return RetrievalQA.from_chain_type(
        llm=llm_client.llm,
        retriever=retriever.retriever,
        return_source_documents=True
    )

qa_chain = build_qa_chain()

class QueryRequest(BaseModel):
    question: str
    top_k: int = int(os.environ.get("TOP_K", 5))

class QueryResponse(BaseModel):
    answer: str
    sources: list
    latency_ms: int

def admin_auth(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != os.environ.get("ADMIN_TOKEN", "admin_secret"):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.on_event("startup")
def auto_reindex():
    def reindex():
        docs = ingest_pdfs(os.environ["DOCS_RAW_DIR"])
        embedder.embed_and_store(docs)
        global retriever, qa_chain
        retriever = Retriever()
        qa_chain = build_qa_chain()
        logger.info("Auto reindex completed on startup.")
    threading.Thread(target=reindex, daemon=True).start()

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    global qa_chain
    start = time.time()
    # cache_key = f"qa:{req.question}:{req.top_k}"
    # cached = redis_client.get(cache_key)
    # if cached:
    #     result = JSONResponse(content=eval(cached))
    #     result.headers["X-Cache"] = "HIT"
    #     return result
    # Use retriever with relevance scores if available
    if hasattr(retriever, "search_with_relevance_scores"):
        docs_and_scores = retriever.search_with_relevance_scores(req.question, top_k=req.top_k)
        # New output: list of dicts with 'content', 'source', 'score'
        source_docs = [d["content"] for d in docs_and_scores]
        doc_score_map = {d["source"]: d["score"] for d in docs_and_scores}
    else:
        source_docs = retriever.search(req.question, top_k=req.top_k)
        doc_score_map = {}
    # If your QA chain expects Document objects, you may need to adapt here
    response = qa_chain({"query": req.question, "source_documents": source_docs})
    answer = response["result"]
    sources = []
    # Compose sources for frontend
    for d in docs_and_scores:
        source_info = {
            "source": d["source"],
            "score": d["score"]
            # Optionally include 'content': d["content"]
        }
        sources.append(source_info)
    latency = int((time.time() - start) * 1000)
    resp = {"answer": answer, "sources": sources, "latency_ms": latency}
    # redis_client.set(cache_key, str(resp), ex=3600)
    return resp

@app.post("/admin/reindex")
async def admin_reindex(request: Request):
    admin_auth(request)
    docs = ingest_pdfs(os.environ["DOCS_RAW_DIR"])
    embedder.embed_and_store(docs)
    global retriever, qa_chain
    retriever = Retriever()
    qa_chain = build_qa_chain()
    return {"status": "reindexed"}

@app.post("/admin/reindex-sse")
async def admin_reindex_sse(request: Request):
    import asyncio
    async def event_generator():
        yield {"event": "progress", "data": "Starting reindex..."}
        try:
            docs = ingest_pdfs(os.environ["DOCS_RAW_DIR"])
            yield {"event": "progress", "data": f"Ingested {len(docs)} documents."}
            embedder.embed_and_store(docs)
            yield {"event": "progress", "data": "Embedded and stored documents."}
            global retriever, qa_chain
            retriever = Retriever()
            qa_chain = build_qa_chain()
            yield {"event": "done", "data": "Reindexing complete!"}
        except Exception as e:
            yield {"event": "error", "data": str(e)}
    return EventSourceResponse(event_generator())

@app.post("/admin/upload")
async def admin_upload(request: Request, file: UploadFile = File(...)):
    admin_auth(request)
    raw_dir = os.environ["DOCS_RAW_DIR"]
    file_path = os.path.join(raw_dir, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    docs = ingest_pdfs(raw_dir)
    embedder.embed_and_store(docs)
    global retriever, qa_chain
    retriever = Retriever()
    qa_chain = build_qa_chain()
    return {"status": "uploaded", "filename": file.filename}

@app.delete("/admin/document/{doc_id}")
async def admin_delete_document(doc_id: str, request: Request):
    admin_auth(request)
    raw_dir = os.environ["DOCS_RAW_DIR"]
    for fname in os.listdir(raw_dir):
        if fname.startswith(doc_id):
            os.remove(os.path.join(raw_dir, fname))
    # Re-ingest after deletion
    docs = ingest_pdfs(raw_dir)
    embedder.embed_and_store(docs)
    global retriever, qa_chain
    retriever = Retriever()
    qa_chain = build_qa_chain()
    return {"status": "deleted", "doc_id": doc_id}

@app.get("/admin/documents")
async def admin_list_documents(request: Request):
    admin_auth(request)
    raw_dir = os.environ["DOCS_RAW_DIR"]
    docs = []
    for fname in os.listdir(raw_dir):
        if fname.lower().endswith(".pdf"):
            docs.append(fname)
    return {"documents": docs}

@app.exception_handler(Exception)
async def sentry_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
