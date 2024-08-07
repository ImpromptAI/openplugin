from abc import ABC, abstractmethod
from typing import List, Optional

from ..config import Config
from ..function_providers import FunctionProvider
from ..messages import Message
from ..plugin import Plugin
from ..plugin_detected import SelectedPluginsResponse


class PluginSelector(ABC):
    """Abstract base class for plugin selectors."""

    def __init__(
        self,
        plugins: List[Plugin],
        config: Optional[Config],
        function_provider: Optional[FunctionProvider],
    ):
        """
        Initialize the plugin selector.
        Args:
            plugins (List[Plugin]): List of plugins to be used by the plugin selector.
            config (Optional[Config]): Additional configuration for the plugin selector.
            llm (Optional[LLM]): Additional language model for the plugin selector.
        """
        self.plugins = plugins
        self.config = config
        self.function_provider = function_provider

    def get_plugin_by_name(self, name: str):
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    @abstractmethod
    def run(self, messages: List[Message]) -> SelectedPluginsResponse:
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
