from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from .plugin import Plugin


class PluginDetected(BaseModel):
    """
    Represents the result of a plugin operation.
    """

    plugin: Plugin
    api_called: Optional[str]
    path: Optional[str]
    method: Optional[str]


class PluginDetectedParams(PluginDetected):
    mapped_operation_parameters: Optional[Dict] = None


class SelectedPluginsResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    final_text_response: Optional[str]
    detected_plugin: Optional[str]
    # detected_plugin_operations: Optional[List[PluginDetected]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]


class SelectedApiSignatureResponse(BaseModel):
    """
    Represents the response from executing prompts.
    """

    run_completed: bool
    modified_input_prompt: Optional[str]
    final_text_response: Optional[str]
    detected_plugin_operations: Optional[List[PluginDetectedParams]]
    response_time: Optional[float]
    tokens_used: Optional[int]
    llm_api_cost: Optional[float]
    llm_calls: Optional[List[Dict]]
    function_request_json: Optional[Union[Dict, List]] = None
    function_response_json: Optional[Union[Dict, List]] = None
    x_dep_tracing: Optional[List] = None
    response_obj_200: Optional[Dict] = None
    system_prompt: Optional[str] = None
    conversations: Optional[List] = None
    examples: Optional[List] = None
