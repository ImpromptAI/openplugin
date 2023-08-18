======================
Documentation
======================


Summary
=========================
This project provides a standard way to define LLM plugins and present them to various LLM engines. It is vendor neutral and meant to facilitate plugin portability across vendors and projects. The project introduces the OpenPlugin manifest file format, which allows developers to specify properties and settings for their plugins such as name, version, dependencies, and supported platforms. This format enables seamless integration with plugin platform providers.

OpenPlugin addresses the problem of mapping natural language instructions to API calls. It involves using a tool selector to determine the intent of the command and mapping it to an API.
Our reference implementation also evaluates the accuracy of the tool selector:

- selecting the correct plugin,
- selecting the correct API operation,
- filling in API parameters correctly, and
- monitoring the cost and round-trip latency of solving the problem


Finally, the project offers plugin platform providers a standardized interface for tool selection, including an LLM Tool Selector API, along with bindings and SDKs. The project provides a hosted instance of the Tool Selector API for demo purposes. Users are encouraged to run / host their own service for production.

Terminology
=========================
Since OpenPlugin exists within a rapidly evolving domain, the terms relating to its design space are similarly evolving. Within the context of OpenPlugin, the following are the relevant terms and their meanings:


**1. Plugin:**
A set of capabilities made available to LLM, typically added by an end user to a chat app or a similar LLM client, to leverage external systems via their APIs.

**2. Plugin Manifest:**
A file in OpenPlugin-defined format containing metadata associated with a plugin that defines capabilities provided by the plugin and how to access them.

**3. Tool Selector:**
An OpenPlugin component that determines a plugin and an operation within its scope that are most relevant to a natural language request. OpenPlugin provides several tool selector implementations, but its architecture is designed to encourage solutions tailored to distinct vendor and model capabilities.

**4. Tool Selector API/Binding:**
The mechanism by which tool selector implementations are introduced into the OpenPlugin framework. Two such mechanisms are currently supported: remove via a REST API and local via a language-specific binding (SDK).



.. toctree::
    :titlesonly:

    plugin_developers/index
    plugin_platform_providers/index
    GitHub Repo <https://github.com/ImpromptAI/openplugin>


.. important::

    This documentation was generated on |today|.
