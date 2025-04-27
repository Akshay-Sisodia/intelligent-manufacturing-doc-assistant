import os
from dotenv import load_dotenv
import structlog
from langchain_groq import ChatGroq

load_dotenv()
logger = structlog.get_logger()

class LLMClient:
    def __init__(self):
        self.api_key = os.environ["GROQ_API_KEY"]
        self.model = os.environ.get("GROQ_MODEL", "llama3-8b-8192")
        assert self.api_key, "GROQ API key must be set in environment!"
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model
        )

    def query(self, prompt: str, context: list, max_tokens: int = 512) -> str:
        system_prompt = (
            "You are a helpful manufacturing documentation assistant. "
            "Answer the user's question using ALL relevant details from the provided context below. "
            "Always provide a complete and comprehensive answer, quoting or including full procedures, steps, or lists from the context if the question asks about them. "
            "If the answer is not in the context, reply: 'I don't know.' Do NOT use outside knowledge. "
            "Cite sources by doc_id and page."
        )
        full_prompt = f"System: {system_prompt}\n\nContext:\n{chr(10).join(context)}\n\nQuestion: {prompt}"
        try:
            result = self.llm.invoke(full_prompt)
            return result
        except Exception as e:
            logger.error("GROQ API call failed", error=str(e))
            return "GROQ API call failed."

if __name__ == "__main__":
    client = LLMClient()
    print(client.query("How to calibrate X-axis encoder?", ["Sample context chunk 1", "Sample context chunk 2"]))
