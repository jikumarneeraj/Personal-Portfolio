import logging
import uuid
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.graph import portfolio_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("neeraj_portfolio_assistant.main")

# Rate limiter: max 30 requests per minute per visitor IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Neeraj's AI Assistant API",
    description="Production LangGraph + Google Gemini agent backend for Neeraj Kumar's portfolio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
cors_origins = settings.get_cors_origins()
logger.info(f"Configuring CORS with allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request & Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's query or message")
    thread_id: Optional[str] = Field(None, description="Client session thread ID for conversational memory")

class ChatResponse(BaseModel):
    response: str
    type: str = "text"
    url: Optional[str] = None
    quick_actions: Optional[List[str]] = None

@app.get("/health", tags=["System"])
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit("30/minute")
async def chat_endpoint(request: Request, body: ChatRequest):
    """
    Chat endpoint for interacting with Neeraj's AI Portfolio Assistant.
    Coordinates intent classification, lightweight RAG, Gemini response generation,
    verified links, and multi-turn contact submission.
    """
    user_message = body.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Generate session thread ID if omitted
    thread_id = body.thread_id.strip() if body.thread_id and body.thread_id.strip() else f"session-{uuid.uuid4().hex[:8]}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        # Run through LangGraph workflow
        result = portfolio_agent.invoke(
            {
                "query": user_message,
                "messages": [{"role": "user", "content": user_message}]
            },
            config=config
        )

        response_text = result.get("response") or "I'm sorry, I couldn't generate a response. Please try again."
        response_type = result.get("response_type") or "text"
        url = result.get("url")
        quick_actions = result.get("quick_actions")

        return ChatResponse(
            response=response_text,
            type=response_type,
            url=url,
            quick_actions=quick_actions
        )

    except Exception as e:
        logger.error(f"Error processing chat in thread {thread_id}: {e}", exc_info=True)
        # Friendly response without leaking internal traceback
        return ChatResponse(
            response="I encountered a temporary problem while processing your message. Please try asking again or use the Contact Us form directly.",
            type="text",
            quick_actions=["About Neeraj", "Projects", "Skills", "Resume"]
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
