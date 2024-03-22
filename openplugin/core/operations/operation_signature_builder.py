from abc import ABC, abstractmethod
from typing import List, Optional

from ..llms import LLM, Config
from ..messages import Message
from ..plugin import Plugin
from ..plugin_detected import SelectedApiSignatureResponse


class OperationSignatureBuilder(ABC):
    """Abstract base class for plugin selectors."""

    def __init__(
        self,
        plugin: Plugin,
        llm: LLM,
        config: Optional[Config],
        pre_prompts: Optional[List[Message]] = None,
        selected_operation: Optional[str] = None,
    ):
        """
        Initialize the plugin selector.
        Args:
            plugin (Plugin): Plugin to be used by the plugin selector.
            config (Optional[Config]): Additional configuration for the plugin selector.
            llm (Optional[LLM]): Additional language model for the plugin selector.
            selected_operation (Optional[str]): Name of the operation to be used by
            the plugin selector.
        """
        self.plugin = plugin
        self.config = config
        self.llm = llm
        self.pre_prompts = pre_prompts
        self.selected_operation = selected_operation

    @abstractmethod
    def run(self, messages: List[Message]) -> SelectedApiSignatureResponse:
        """
        Run the plugin selector on the given list of messages and return a response.
        This method should be implemented by the derived classes.
        Args:
            messages (List[Message]): List of messages to be processed by the selector.
        Returns:
            Response: The response generated by the plugin selector.
        """
        pass

    @classmethod
    @abstractmethod
    def get_pipeline_name(cls) -> str:
        pass
