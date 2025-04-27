import re
from typing import List, Dict
import structlog

logger = structlog.get_logger()

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def attach_metadata(chunk: str, doc_id: str, page_num: int) -> Dict:
    return {"text": chunk, "doc_id": doc_id, "page": page_num}
