import os
from typing import Optional, Dict, Any
from llama_cpp import Llama
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger("mistral_integration")

def load_mistral_model(
    model_path: str = os.getenv("MISTRAL_MODEL_PATH"),
    **kwargs: Dict[str, Any]
) -> Optional[Llama]:
    """Load Mistral model with environment-configured parameters"""
    try:
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        config = {
            "model_path": model_path,
            "n_ctx": int(os.getenv("MODEL_CTX", "2048")),
            "n_gpu_layers": int(os.getenv("GPU_LAYERS", "35")),
            "n_threads": int(os.getenv("THREADS", "6")),
            "n_threads_batch": int(os.getenv("THREADS_BATCH", "6")),
            "offload_kqv": os.getenv("OFFLOAD_KQV", "True") == "True",
            "use_mmap": os.getenv("USE_MMAP", "False") == "True",
            "use_mlock": os.getenv("USE_MLOCK", "False") == "True",
            "flash_attn": os.getenv("FLASH_ATTN", "True") == "True",
            "verbose": False,
            **kwargs
        }

        logger.info("Loading Mistral model with config: %s", {k: v for k, v in config.items() if k != 'model_path'})
        return Llama(**config)
    
    except Exception as e:
        logger.error("Model loading failed: %s", str(e), exc_info=True)
        return None

if __name__ == "__main__":
    model = load_mistral_model()
    if model:
        print("✅ Mistral model loaded successfully!")
    else:
        print("❌ Failed to load Mistral model. Check logs for details.")