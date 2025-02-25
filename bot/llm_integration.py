from transformers import pipeline
import torch
import concurrent.futures

# Load the model once at startup
model_name = "microsoft/DialoGPT-small"
device = "cuda" if torch.cuda.is_available() else "cpu"
device_index = 0 if device == "cuda" else -1
generator = pipeline('text-generation', model=model_name, tokenizer=model_name, device=device_index)

def fetch_llm_answer(query: str) -> str:
    """
    Generate a response using the loaded LLM model.
    """
    try:
        result = generator(query, max_length=150, do_sample=True, temperature=0.7, truncation=True)
        return result[0]['generated_text'].strip()
    except Exception as e:
        return f"Error retrieving LLM response: {str(e)}"

def fetch_llm_answer_with_timeout(query: str, timeout: float = 0.5) -> str:
    """
    Attempts to get an LLM response within the specified timeout (default 0.5 seconds).
    If the response isn't generated in time, returns a fallback message.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_llm_answer, query)
        try:
            answer = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            answer = ("LLM response is taking too long. "
                      "Please contact human support for further assistance.")
    return answer
