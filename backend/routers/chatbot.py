from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.concurrency import run_in_threadpool
from typing import Optional, Dict
import os
import re
import logging
import time
import threading
from llama_cpp import Llama
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from llm.mistral_integration import load_mistral_model

load_dotenv()

logger = logging.getLogger("chatbot")
router = APIRouter()

# Constants
MAX_INPUT_LENGTH = 500
MODEL_DEFAULTS = {
    "max_tokens": 150,
    "temperature": 0.5,
    "top_p": 0.9,
    "repeat_penalty": 1.1
}

# Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    max_tokens: Optional[int] = Field(None, ge=10, le=500)
    temperature: Optional[float] = Field(None, ge=0.1, le=1.0)
    top_p: Optional[float] = Field(None, ge=0.1, le=1.0)

    @field_validator('message')
    def validate_message(cls, v):
        return sanitize_input(v)

class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    processing_time: float
    tokens_per_sec: float
    model_status: Dict[str, str]

# Global state with thread safety
_model_lock = threading.Lock()
_model: Optional[Llama] = None
_system_prompt = """You are a helpful, honest AI assistant. Provide concise answers 
and always maintain a professional tone. If unsure, say you don't know."""

# Model Management
async def initialize_model():
    global _model
    try:
        with _model_lock:
            if not _model:
                _model = await run_in_threadpool(load_mistral_model)
                # Warm up model with empty prompt
                await run_in_threadpool(_model.create_completion, "", max_tokens=1)
                logger.info("Model initialized successfully")
                return True
    except Exception as e:
        logger.error(f"Model initialization failed: {str(e)}")
        raise RuntimeError("Model initialization failed")

async def cleanup_resources():
    with _model_lock:
        if _model:
            await run_in_threadpool(_model.__del__)
            logger.info("Model resources cleaned up")

def get_model() -> Llama:
    if _model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not initialized"
        )
    return _model

def model_status() -> Dict[str, str]:
    return {
        "status": "loaded" if _model else "unloaded",
        "backend": "cuda" if _model and hasattr(_model, 'ctx') else "cpu",
        "context_size": str(_model.n_ctx) if _model else "0"
    }

# Processing Functions
def sanitize_input(text: str) -> str:
    """Secure input handling with allowed characters"""
    cleaned = re.sub(r'[^\w\s,.?!@$%&*()-+=:;\'"<>/\\]', '', text)
    return cleaned.strip()[:MAX_INPUT_LENGTH]

def format_prompt(user_input: str) -> str:
    return f"""<s>[INST] <<SYS>>
{_system_prompt}
<</SYS>>

{user_input} [/INST]"""

# Endpoint
@router.post(
    "/chat", 
    response_model=ChatResponse,
    responses={
        400: {"description": "Invalid input"},
        503: {"description": "Model not available"},
        500: {"description": "Internal processing error"}
    }
)
async def chat_endpoint(request: ChatRequest):
    start_time = time.monotonic()
    try:
        model = get_model()
        params = {
            "max_tokens": request.max_tokens or MODEL_DEFAULTS["max_tokens"],
            "temperature": request.temperature or MODEL_DEFAULTS["temperature"],
            "top_p": request.top_p or MODEL_DEFAULTS["top_p"],
            "repeat_penalty": MODEL_DEFAULTS["repeat_penalty"]
        }

        formatted_prompt = format_prompt(request.message)
        
        output = await run_in_threadpool(
            model.create_completion,
            formatted_prompt,
            **params,
            stop=["</s>", "[INST]"],
            echo=False
        )

        if not output or "choices" not in output:
            logger.error("Invalid model output: %s", output)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model response format invalid"
            )

        raw_response = output['choices'][0]['text'].strip()
        processed_response = re.sub(r'\n+', '\n', raw_response.split('[/INST]')[-1])

        processing_time = time.monotonic() - start_time
        tokens_used = output['usage']['completion_tokens']
        
        return ChatResponse(
            response=processed_response,
            tokens_used=tokens_used,
            processing_time=round(processing_time, 2),
            tokens_per_sec=round(tokens_used / processing_time, 1),
            model_status=model_status()
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Chat processing failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )