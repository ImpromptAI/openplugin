import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


# Decorator for retrying the function with exponential backoff
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(4))
def chat_completion_with_backoff(**kwargs):
    # Check if 'openai_api_key' is in kwargs
    if "openai_api_key" not in kwargs:
        raise ValueError("openai_api_key not in kwargs")
    # Set the OpenAI API key from kwargs
    openai.api_key = kwargs["openai_api_key"]
    kwargs.pop("openai_api_key")
    # Call OpenAI's ChatCompletion.create method with the remaining kwargs
    return openai.ChatCompletion.create(**kwargs)
