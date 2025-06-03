import os
import time
from llama_cpp import Llama
from dotenv import load_dotenv
import logging
import sys

load_dotenv()
MODEL_PATH = os.getenv("MISTRAL_MODEL_PATH")

# Configure logging
logging.basicConfig(level=logging.ERROR)

# System prompt configuration
SYSTEM_PROMPT = """You are a helpful, respectful AI assistant. Provide concise, friendly responses to user queries. Keep answers natural and conversational."""

def format_prompt(user_input: str) -> str:
    """Format the prompt using Mistral's instruction template"""
    return f"""<s>[INST] <<SYS>>
{SYSTEM_PROMPT}
<</SYS>>

{user_input} [/INST]"""

def load_mistral_model():
    """Load the Mistral model with optimized settings"""
    if not os.path.exists(MODEL_PATH):
        logging.error(f"Model not found at {MODEL_PATH}")
        return None

    try:
        return Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,  # Increased context window
            n_gpu_layers=35,
            n_threads=6,
            temperature=0.5,  # More focused responses
            top_p=0.9,
            repeat_penalty=1.1,
            n_threads_batch=6,
            use_mmap=True,
            use_mlock=False,
            flash_attn=True,
            verbose=False,
            log_handler=None
        )
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None

def generate_response(llm, prompt: str) -> str:
    """Generate response with error handling"""
    try:
        output = llm(
            prompt,
            max_tokens=200,
            stop=["</s>", "[INST]"],  # Stop generation tokens
            echo=False
        )
        return output['choices'][0]['text'].strip()
    except Exception as e:
        logging.error(f"Generation error: {e}")
        return "I encountered an error processing your request."

def main():
    # Suppress initial loading logs
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    
    print("\nInitializing Mistral Assistant...")
    start_load = time.time()
    mistral_llm = load_mistral_model()
    load_time = time.time() - start_load
    
    sys.stderr = original_stderr

    if not mistral_llm:
        print("Failed to initialize model. Check model path and permissions.")
        return

    print("\n" + "="*40)
    print("Mistral 7B Chat Assistant (type 'exit' to quit)")
    print(f"Model loaded in {load_time:.2f} seconds")
    print("="*40 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ('exit', 'quit'):
                break
                
            if not user_input:
                print("Please enter a message.")
                continue

            # Format the prompt
            formatted_prompt = format_prompt(user_input)
            
            # Generate response
            start_response = time.time()
            generated_text = generate_response(mistral_llm, formatted_prompt)
            response_time = time.time() - start_response
            
            # Clean and format response
            final_response = generated_text.split('[/INST]')[-1].strip()
            final_response = final_response.replace("<s>", "").replace("</s>", "")

            # Print formatted output
            print("\nAssistant:")
            print(final_response)
            print(f"\n[Response time: {response_time:.2f}s | Tokens: {len(final_response.split())}]")
            print("-"*50 + "\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue

if __name__ == "__main__":
    main()