import os
import base64
import structlog
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
logger = structlog.get_logger()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# Initialize Mistral SDK client
client = Mistral(api_key=MISTRAL_API_KEY)

def encode_pdf(pdf_path):
    """Encode the pdf to base64."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except FileNotFoundError:
        logger.error(f"Error: The file {pdf_path} was not found.")
        return None
    except Exception as e:
        logger.error(f"Error encoding PDF: {e}")
        return None

def mistral_ocr_extract(pdf_file: str):
    base64_pdf = encode_pdf(pdf_file)
    if not base64_pdf:
        logger.error("Base64 encoding failed", file=pdf_file)
        return []
    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}"
            }
        )
        # Try extracting pages from multiple possible keys
        pages = ocr_response.pages
        processed_pages = []
        for page in pages:
            # Each page should have 'index' and 'markdown'
            page_number = page.index
            content = page.markdown
            if page_number is None:
                page_number = 1  # fallback
            if content is None:
                content = ""
            processed_pages.append({
                "page_number": page_number,
                "content": content
            })
        logger.info("Mistral OCR SDK response", file=pdf_file, num_pages=len(processed_pages))
        return processed_pages
    except Exception as e:
        logger.error("Mistral OCR SDK failed", file=pdf_file, error=str(e))
        return []

def ingest_pdfs(raw_dir: str) -> list:
    pdf_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.lower().endswith('.pdf')]
    logger.info("PDF files found for ingestion", pdf_files=pdf_files)
    processed = []
    for pdf_file in pdf_files:
        doc_id = os.path.splitext(os.path.basename(pdf_file))[0]
        pages = mistral_ocr_extract(pdf_file)
        for page in pages:
            text = page.get("content")
            page_num = page.get("page_number")
            if text and text.strip():
                processed.append({
                    "text": text,
                    "doc_id": doc_id,
                    "page": page_num
                })
    logger.info("Loaded documents with Mistral OCR", num_docs=len(processed))
    return processed

if __name__ == "__main__":
    docs = ingest_pdfs(os.environ["DOCS_RAW_DIR"])
    print(f"Loaded {len(docs)} documents.")
