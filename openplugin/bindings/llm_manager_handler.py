import ast
import json
import os

import boto3
import litellm
import vertexai
from google.oauth2 import service_account

AWS_MODELS = [
    "anthropic.claude-v1",
    "anthropic.claude-instant-v1",
    "anthropic.claude-v2",
    "ai21.j2-mid-v1",
    "ai21.j2-ultra-v1",
]


def get_llm_response_from_messages(
    msgs,
    model,
    llm_api_key,
    temperature: float = 0,
    max_tokens: int = 2048,
    top_p: float = 1,
    frequency_penalty=0,
    presence_penalty=0,
    aws_access_key_id=None,
    aws_region_name=None,
):
    if model.lower() in AWS_MODELS and aws_access_key_id and aws_region_name:
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=llm_api_key,
        )
        response = litellm.completion(
            messages=msgs,
            aws_bedrock_client=bedrock,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        cost = litellm.completion_cost(completion_response=response)
        return {
            "response": response["choices"][0].get("message").get("content"),
            "usage": response.get("usage").get("total_tokens"),
            "cost": float(cost),
        }

    if "bison" in model:
        google_key = llm_api_key
        if isinstance(google_key, str):
            google_key = ast.literal_eval(google_key)

        credentials = service_account.Credentials.from_service_account_info(
            google_key
        )
        vertexai.init(
            project=os.environ["GOOGLE_PROJECT_NAME"],
            location=os.environ["GOOGLE_PROJECT_LOC"],
            credentials=credentials,
        )
    else:
        litellm.api_key = llm_api_key
    litellm.drop_params = True
    response = litellm.completion(
        model=model,
        messages=msgs,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    cost = litellm.completion_cost(completion_response=response)
    # formatted_string = f"${float(cost):.10f}"
    return {
        "response": response["choices"][0].get("message").get("content"),
        "usage": response.get("usage").get("total_tokens"),
        "cost": float(cost),
    }
