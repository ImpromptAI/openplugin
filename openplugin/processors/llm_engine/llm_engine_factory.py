from ..processor import ProcessorImplementationType
from .llm_engine import LLMEngine


def get_llm_engine(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> LLMEngine:
    if implementation_type == ProcessorImplementationType.LLM_ENGINE_WITH_OPENAI:
        from .implementations.llm_engine_with_openai import LLMEngineWithOpenAI

        return LLMEngineWithOpenAI(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
