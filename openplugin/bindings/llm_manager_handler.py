import litellm


def get_llm_response_from_messages(
    msgs,
    model,
    llm_api_key,
    temperature: float = 0,
    max_tokens: int = 2048,
    top_p: float = 1,
    frequency_penalty=0,
    presence_penalty=0,
):
    litellm.api_key = llm_api_key
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
