=================
Getting Started
=================

Table of Contents
-----------------

.. contents::
   :local:
   :depth: 2


About
===================

Openplugin is an open-source platform that allows developers to create, share, and run plugins. It is a platform that enables developers to build plugins using the OpenAPI specification and run them on the Openplugin server. The platform is designed to be extensible and allows developers to create plugins that can be used with different LLMs.


Lifecycle of a plugin
======================

The lifecycle of a plugin can be divided into four primary stages:

**1. Build a Plugin:**

This stage involves the construction of a plugin manifest from the openapi specification.

To begin with plugin building, refer to this guide: :ref:`build-plugins-getting-started`


**2. Call a Plugin:**

After the plugin is built, it has to be invoked or called. This process involves sending a request to the openplugin server with the user prompt and the openplugin manifest. A plugin can be invoked using an HTTP request or by utilizing the openplugin-sdk.

To start invoking a plugin, refer to this guide: :ref:`call-plugins-getting-started`

**3. Host a Plugin:**

This stage involves supplying a platform for the plugin to run. You can either use Imprompt openplugin server or host your own.

To begin with plugin hosting, refer to this guide: :ref:`host-plugins-getting-started`


**4. Find a Plugin:**

This stage involves making your newly created plugin discoverable on platforms like Github or the Imprompt marketplace.

To start discovering plugins, refer to this guide: :ref:`find-plugins-getting-started`


