======================
Documentation
======================


.. image:: _images/openplugin_logo.jpg
    :alt: Logo

Summary
=========================
This project provides a standard way to define LLM plugins. It is vendor neutral, and meant to be used across vendors and projects.  The project introduces the OpenPlugin manifest file format, which allows developers to specify properties and settings for their plugins such as name, version, dependencies, and supported platforms. This format enables seamless integration with plugin platform providers.

OpenPlugin addresses the problem of mapping natural language instructions to API calls. It involves using a tool selector to determine the intent of the command and map it to an API.
Our reference implementation also evaluates the accuracy of the tool selector:

- selecting the correct plugin,
- selecting the correct API operation,
- filling in API parameters correctly, and
- monitoring the cost and round-trip latency of solving the problem


Finally, the project offers plugin platform providers a standardized interface for tool selection, including an LLM Tool Selector API, along with bindings and SDKs. The project provides a hosted instance of the Tool Selector API for demo purposes. Users are encouraged to run / host their own service for production.

Terminology
=========================
Unfortunately, as this is an emerging space, there are lots of competing terms floating around. Specific to this project, here are the definitions we’re using:


**1. Plugin:**
First, it’s assumed that we mean “an LLM plugin”. A plugin is the technology an end user would add to a chat app or similar to leverage 3rd party tools like APIs.

**2. Plugin Manifest:**
This is the metadata associated with a plugin that users or programs can view to determine how to install it, and call it.

**3. Tool Selector:**
This refers to solutions that execute the natural language and map it to an API. Typically this is done by a platform vendor (Microsoft, Google, HuggingFace) or a library (LangChain, Imprompt).

**4. Tool Selector API/ Bindings:**
The process of mapping natural language to a tool can be modularized, and made a dedicated task. This task can be called via a RESTful API call, or locally via a language specific binding (SDK).




.. toctree::
    :titlesonly:

    plugin_developers/index
    plugin_platform_providers/index
    Github Repo <https://github.com/LegendaryAI/openplugin>


.. important::

    This documentation was generated on |today|.
