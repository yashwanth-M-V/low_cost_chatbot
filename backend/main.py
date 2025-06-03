from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from routers import chatbot
import os
import time
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage model lifecycle efficiently"""
    logging.info("Initializing AI model...")
    start_time = time.time()
    
    try:
        # Initialize model in parallel thread to avoid blocking
        await chatbot.initialize_model()
        load_time = time.time() - start_time
        logging.info(f"Model loaded in {load_time:.2f} seconds")
    except Exception as e:
        logging.error(f"Model initialization failed: {str(e)}")
        raise
    
    yield  # App is running here
    
    logging.info("Cleaning up resources...")
    await chatbot.cleanup_resources()

app = FastAPI(
    title="Mistral 7B API",
    description="Optimized Production API for Mistral-7B LLM",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store, max-age=0",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    })
    return response

# Include routers
app.include_router(
    chatbot.router,
    prefix="/api/v1/chat",
    tags=["AI Chat"],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Model not loaded"}
    }
)


# Health Check Endpoint
@app.get(
    "/api/health",
    summary="Service Health Check",
    tags=["System"],
    response_description="Service status information"
)
async def health_check():
    return {
        "status": "ok" if chatbot.is_model_loaded() else "unhealthy",
        "timestamp": time.time(),
        "model_status": chatbot.model_status(),
        "api_version": app.version
    }

# Root Endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Mistral 7B API is operational"}

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info"),
        reload=os.getenv("RELOAD", "False").lower() == "true"
    )