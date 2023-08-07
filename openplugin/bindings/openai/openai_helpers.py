import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(4))
def chat_completion_with_backoff(**kwargs):
    if 'openai_api_key' not in kwargs:
        raise ValueError('openai_api_key not in kwargs')
    openai.api_key = kwargs['openai_api_key']
    kwargs.pop('openai_api_key')
    return openai.ChatCompletion.create(**kwargs)
