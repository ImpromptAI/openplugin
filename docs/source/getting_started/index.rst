=================
Introduction
=================


-----------------

.. contents::
   :local:
   :depth: 2


**What is OpenPlugin?** 

===================

Today, developers can interact with APIs using natural language, often referred to as "function calling" or "tool use." As this concept gains widespread adoption, OpenPlugin builds upon function calling to enable an ecosystem of plugin providers.

Key Concepts:

1. **LLM Neutrality**: Ensure the plugins are compatible with various large language models (LLMs), such as those from Cohere, OpenAI, Anthropic, and others, allowing for seamless integration across different AI platforms.

2. **Standardized Plugin Manifest**: Establish a standardized format for plugin metadata, making it easier to discover, install, and manage a vast repository of ready-to-use plugins.

3. **Expanded Function Calling Capabilities**: Extend the core function calling feature with a comprehensive set of common helper functions that developers frequently require, streamlining the development process and reducing the need for custom implementations.

By addressing these key concepts, OpenPlugin aims to create a robust and versatile ecosystem that empowers developers to leverage the power of AI-driven function calling, unlocking new possibilities in software development and integration.


===================

**The Core Elements of the OpenPlugin Platform:**

1. **OpenPlugin Manifest**: A standardized, machine-readable format to describe the metadata and capabilities of plugins, enabling seamless discovery, installation, and integration across different AI platforms and development environments.

2. **OpenPlugin Server**: An open-source server that securely executes plugins on behalf of developers, providing a reliable and scalable infrastructure for running plugin-powered applications.

3. **OpenPlugin SDK**: A set of convenience libraries (e.g., Python, JavaScript) that abstract the underlying REST interface, making it easier for developers to integrate and utilize plugins within their preferred programming languages and development workflows.

4. **OpenPlugin Catalog Repositories**: A network of publicly accessible repositories (e.g., GitHub) that store the descriptors for a wide range of available plugins, allowing developers to discover, evaluate, and incorporate the functionality they need into their applications.

OpenPlugin aims to create a cohesive and extensible ecosystem that empowers developers to leverage the power of AI-driven functionality, while ensuring interoperability, security, and ease of use across diverse development environments and AI platforms.


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
