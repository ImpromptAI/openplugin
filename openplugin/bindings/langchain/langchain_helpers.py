# TODO: OUTDATED, needs to be updated to use the new plugin system
"""
import os

from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

from openplugin.interfaces.models import LLM


def get_agent_type(pipeline_name: str) -> AgentType:
    if pipeline_name == "zero-shot-react-description":
        return AgentType.ZERO_SHOT_REACT_DESCRIPTION
    elif pipeline_name == "react-docstore":
        return AgentType.REACT_DOCSTORE
    elif pipeline_name == "self-ask-with-search":
        return AgentType.SELF_ASK_WITH_SEARCH
    elif pipeline_name == "conversational-react-description":
        return AgentType.CONVERSATIONAL_REACT_DESCRIPTION
    elif pipeline_name == "chat-zero-shot-react-description":
        return AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION
    elif pipeline_name == "chat-conversational-react-description":
        return AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
    elif pipeline_name == "structured-chat-zero-shot-react-description":
        return AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
    raise ValueError(f"Pipeline name {pipeline_name} not supported")


def get_llm(llm: LLM, api_key: str):
    if llm is None:
        raise ValueError("LLM is not set.")
    if llm.provider.lower() =="openai":
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = api_key
        return OpenAI(
            model=llm.model_name,
            temperature=llm.temperature,
            max_tokens=llm.max_tokens,
            top_p=llm.top_p,
            frequency_penalty=llm.frequency_penalty,
            presence_penalty=llm.presence_penalty,
            n=llm.n,
            best_of=llm.best_of,
            client=None,
        )
    elif llm.provider.lower() == "openai":
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = api_key
        return ChatOpenAI(
            model=llm.model_name,
            temperature=llm.temperature,
            max_retries=llm.max_retries,
            n=llm.n,
            max_tokens=llm.max_tokens,
            client=None,
        )
    raise ValueError(f"LLM provider {llm.provider} not supported")
"""
