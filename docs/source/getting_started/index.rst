=================
Introduction
=================

.. contents::
   :local:
   :depth: 2


**What is OpenPlugin?**

=============================

Today, developers can interact with APIs using natural language, often referred to as "function calling" or "tool use." As this concept gains widespread adoption, OpenPlugin builds upon function calling to enable an ecosystem of plugin providers.

Key Concepts:

1. **LLM Neutrality**: Ensure the plugins are compatible with various large language models (LLMs), such as those from Cohere, OpenAI, Anthropic, and others, allowing for seamless integration across different AI platforms.

2. **Standardized Plugin Manifest**: Establish a standardized format for plugin metadata, making it easier to discover, install, and manage a vast repository of ready-to-use plugins.

3. **Expanded Function Calling Capabilities**: Extend the core function calling feature with a comprehensive set of common helper functions that developers frequently require, streamlining the development process and reducing the need for custom implementations.

By addressing these key concepts, OpenPlugin aims to create a robust and versatile ecosystem that empowers developers to leverage the power of AI-driven function calling, unlocking new possibilities in software development and integration.


===================

**The OpenPlugin Platform**

1. **OpenPlugin Manifest**: A standardized, machine-readable format to describe the metadata and capabilities of plugins, enabling seamless discovery, installation, and integration across different AI platforms and development environments.

2. **OpenPlugin Server**: An open-source server that securely executes plugins on behalf of developers, providing a reliable and scalable infrastructure for running plugin-powered applications.

3. **OpenPlugin SDK**: A set of convenience libraries (e.g., Python, JavaScript) that abstract the underlying REST interface, making it easier for developers to integrate and utilize plugins within their preferred programming languages and development workflows.

4. **OpenPlugin Catalog Repositories**: A network of publicly accessible repositories (e.g., GitHub) that store the descriptors for a wide range of available plugins, allowing developers to discover, evaluate, and incorporate the functionality they need into their applications.



===================


**Building LLM Plugins**

Creating your own plugins is a straightforward process. The best way to get started is by cloning an existing plugin and modifying it to suit your needs.

For a quick start guide on building plugins, refer to: :ref:`build-plugins-getting-started`

**Calling a Plugin**

Once you have a plugin manifest ready, you can send it to the OpenPlugin server along with your prompt. Plugins can be invoked using an HTTP request or by leveraging the `openplugin-sdk`.

To learn more about calling plugins, check out: :ref:`call-plugins-getting-started`

**Discovering Existing Plugins**

To make your newly created plugin discoverable, you can publish it on platforms like GitHub or the Imprompt marketplace.

To start exploring the available plugins, refer to: :ref:`find-plugins-getting-started`

**Hosting Your Own Plugin Server** (Optional)

If you prefer, you can run your own OpenPlugin server and make it publicly accessible on the internet or keep it private behind your firewall.

For guidance on hosting your own plugin server, check out: :ref:`host-plugins-getting-started`

Alternatively, if you'd like to use a public server, you can visit https://app.imprompt.ai and access the Plugin Builder from the main menu.
