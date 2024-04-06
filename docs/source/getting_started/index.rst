=================
Introduction
=================


-----------------

.. contents::
   :local:
   :depth: 2


**What is OpenPlugin?** 

===================

Today, developers can call API's via natural language (often called 'function calling', 'tool use', etc.) As this concept becomes widely adopted, OpenPlugin builds on top of function calling to enable an ecosystem of plugin providers. 

**Key Concepts**:

1: Make the plugins LLM neutral (works across Cohere, OpenAI, Anthropic, etc.) 

2: Standardize the plugin manifest and create a HUGE repository of ready-to-go plugins

3: Extend the core function calling with the common helper functions that you constantly need  


===================


The core elements are:

- **The OpenPlugin Manifest** - a standardized format to describe plugins

- **The OpenPlugin Server** - an open source server that executes the plugins  

- **The OpenPlugin SDK** - a convenience libary (Python, ...) over the REST interface 

- **The OpenPlugin Catalog Repos** - store public plugin descriptors in Github 



===================



**1. Building LLM Plugins:**

Anyone can create thier own plugins. Most people start by cloning an existing one, and editing it.  

Here's a quick start guide: :ref:`build-plugins-getting-started`


**2. Call a Plugin:**

After a plugin manifest is built, you send it to the OpenPlugin server with the your prompt. A plugin can be invoked using an HTTP request or by utilizing the openplugin-sdk.

To call a plugin, refer to this guide: :ref:`call-plugins-getting-started`


**3. Find Existing Plugin:**

This stage involves making your newly created plugin discoverable on platforms like Github or the Imprompt marketplace.

To start discovering plugins, refer to this guide: :ref:`find-plugins-getting-started`

**4. Host Your Own Plugin Sever:** (optional)  

Run your own OpenPlugin server - make it public on the Internet, or private behind your firewall. 

If you want to host your own server, refer to this guide: :ref:`host-plugins-getting-started`

If you'd prefer to use a public server, check out: https://app.imprompt.ai and open the Plugin Builder from the main menu. 
