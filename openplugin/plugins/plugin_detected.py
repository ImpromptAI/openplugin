from typing import Dict, List, Optional

from pydantic import BaseModel

from .plugin import Plugin


class PluginDetected(BaseModel):
    """
    Represents the result of a plugin operation.
    """

    plugin: Plugin
    api_called: Optional[str]
    method: Optional[str]


class PluginDetectedParams(PluginDetected):
    mapped_operation_parameters: Optional[Dict] = None


class SelectedPluginsResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetected]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class SelectedApiSignatureResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetectedParams]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]
    llm_calls: Optional[List[Dict]]
