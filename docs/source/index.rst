======================
Documentation
======================


.. image:: _images/openplugin_logo.jpg
    :alt: Logo

Summary
=========================


Terminology
=========================
Unfortunately, as this is an emerging space, there are lots of competing terms floating around. Specific to this project, here are the definitions we’re using:


**1. Plugin**
First, it’s assumed that we mean “an LLM plugin”. A plugin is the technology an end user would add to a chat app or similar to leverage 3rd party tools like APIs.

**2. Plugin Manifest**
This is the metadata associated with a plugin that users or programs can view to determine how to install it, and call it.

**3. Tool Selector**
This refers to solutions that execute the natural language and map it to an API. Typically this is done by a platform vendor (Microsoft, Google, HuggingFace) or a library (LangChain, Imprompt).

**4. Tool Selector API/ Bindings**
The process of mapping natural language to a tool can be modularized, and made a dedicated task. This task can be called via a RESTful API call, or locally via a language specific binding (SDK).



The OpenPlugin Project
========================

.. toctree::
    :titlesonly:

    plugin_developers/index
    plugin_platform_providers/index
    Github Repo <https://github.com/LegendaryAI/openplugin>


.. important::

    This documentation was generated on |today|.

