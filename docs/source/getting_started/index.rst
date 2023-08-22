=================
Getting Started
=================

.. toctree::


Installing Dependencies
=======================

OpenPlugin uses Poetry to manage dependencies. See https://github.com/python-poetry/install.python-poetry.org for universal installation instructions. Once Poetry is available on your system, run ``poetry install`` in the root directory of your OpenPlugin Git workspace.


Starting API Server
===================

OpenPlugin comes with a simple REST API server. An OpenAI API key is required to use it with OpenAI-based plugin selectors. It can be supplied to the OpenPlugin API server via ``OPENAI_API_KEY`` environment variable or via ``.env`` file in the root directory of the OpenPlugin Git workspace. The latter method is preferable for our purposes, as it facilitates reproducibility of the runtime environment and allows for preservation of secrecy of the API key better than specifying it in the shell prompt.

The content of your ``.env`` file should be just the following one line:

.. code-block:: text

   OPENAI_API_KEY=<your-OpenAI-API-key>


Make sure to replace ``<your-OpenAI-API-key>`` with the API key from OpenAI. The server can then be started with the following command:

.. code-block:: bash

   poetry run python start_api_server.py


The ``start_api_server.py`` script reads the ``.env`` file to initialize OpenAI-based plugin selectors. If you prefer not to use ``.env`` or already have the ``OPENAI_API_KEY`` variable defined in your environment, you can also run the API server as follows:

.. code-block:: bash

   poetry run openplugin start-server


Note that the above commands are identical for Unix-style shells and PowerShell on both Linux and Windows.


Making A Plugin
===================

We will create a demo plugin for Klarna, a comparison shopping service. An official Klarna LLM plugin is available for OpenAI's ChatGPT, but our Klarna plugin will be usable with any LLM via OpenPlugin.

As with ChatGPT plugins, OpenPlugin consumes a manifest describing the operations available in the API of the service. The manifest contains a reference to the API specification in OpenAPI (Swagger) format along with natural language annotations for each operation, making each operation as clear to the LLM as possible.

Here is the complete OpenPlugin manifest for our Klarna plugin:

.. code-block:: json

    {
      "auth": {
        "type": "none"
      },
      "name": "Klarna Shopping",
      "logo_url": "https://www.klarna.com/assets/sites/5/2020/04/27143923/klarna-K-150x150.jpg",
      "description": "Assistant uses the Klarna plugin to get relevant product suggestions for any shopping or product discovery purpose.",
      "contact_email": "openai-products@klarna.com",
      "legal_info_url": "https://www.klarna.com/us/legal/",
      "schema_version": "v1",
      "openapi_doc_url": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
      "plugin_operations": {
        "/public/openai/v0/products": {
          "get": {
            "human_usage_examples": [
              "Show me some T Shirts.",
              "Show me some pants.",
              "Show me winter jackets for men."
            ],
            "plugin_cleanup_helpers": [
              "Use markdown",
              "Summarize and list the products"
            ],
            "plugin_signature_helpers": []
          }
        }
      }
    }

The details of the manifest format are defined in :ref:`openplugin-manifest`. For our purposes, note the ``plugin_operations`` property in the above JSON: it specifies the API operation used in the following steps. Save the manifest and make it available to your OpenPlugin API server for retrieval via HTTP/S.


Requesting Plugin Selection
===========================

The core of the OpenPlugin functionality is plugin selection. The API server provides an interface to perform this function. The input to the call specifies:

1. User's natural language message that may require the use of a plugin to optimally respond to.
2. Set of plugins to consider.
3. Tool Selector to use.
4. LLM engine and model that would be used by the Tool Selector.

Here is a sample plugin selection call to the API server using ``curl``:

.. code-block:: bash

   curl -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "messages": [{
                "content": "Show me 4 t-shirts",
                "message_type": "HumanMessage"
            }],
            "tool_selector_config": {
                "provider": "OpenAI",
                "pipeline_name": "default"
            },
            "plugins": [{
                "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
            }],
            "config": {},
            "llm": {
                "provider": "OpenAIChat",
                "model_name": "gpt-3.5-turbo-0613"
            }
        }' \
        http://localhost:8006/api/plugin-selector

The value of the ``manifest_url`` property of the JSON request body above should refer to the OpenPlugin manifest created in the previous step.

A successful response will return HTTP response code 200 with a response body that looks as follows:

.. code-block:: json

    {
      "run_completed": true,
      "final_text_response": null,
      "detected_plugin_operations": [
        {
          "plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
            "schema_version": "v1",
            "name": "Klarna Shopping",
            "description": "Assistant uses the Klarna plugin to get relevant product suggestions for any shopping or product discovery purpose.",
            "openapi_doc_url": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
            "auth": {
              "type": "none",
              "authorization_type": null,
              "verification_tokens": null,
              "scope": null,
              "client_url": null,
              "authorization_url": null,
              "authorization_content_type": null,
              "token_validation_url": null
            },
            "logo_url": "https://www.klarna.com/assets/sites/5/2020/04/27143923/klarna-K-150x150.jpg",
            "contact_email": "openai-products@klarna.com",
            "legal_info_url": "https://www.klarna.com/us/legal/",
            "api_endpoints": [
              "https://www.klarna.com/us/shopping/public/openai/v0/products"
            ],
            "plugin_operations": {
              "/public/openai/v0/products": {
                "get": {
                  "human_usage_examples": [
                    "Show me some T Shirts.",
                    "Show me some pants.",
                    "Show me winter jackets for men."
                  ],
                  "prompt_signature_helpers": [],
                  "plugin_cleanup_helpers": [
                    "Use markdown",
                    "Summarize and list the products"
                  ]
                }
              }
            }
          },
          "api_called": "https://www.klarna.com/us/shopping/public/openai/v0/products",
          "method": "get"
        }
      ],
      "response_time": 3.11,
      "tokens_used": 409,
      "llm_api_cost": 0.0
    } 


Requesting Call Signature
=========================

The next OpenPlugin API server operation that is typically invoked after plugin selection is the call signature request. This function produces the specific plugin API call semantics, generating the parameter values for plugin invocation. The request is the same as for the plugin selection, the only difference being the URL path of the API server:

.. code-block:: bash

   curl -X POST \
        -H "Content-Type: application/json" \
        -d '{
          "messages": [{
            "content":"Show me 4 t-shirts",
            "message_type":"HumanMessage"
          }],
          "tool_selector_config": {
            "provider":"OpenAI",
            "pipeline_name":"default"
          },
          "plugin": {
            "manifest_url":"https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json"
          },
          "config": {},
          "llm": {
            "provider":"OpenAIChat",
            "model_name":"gpt-3.5-turbo-0613"
          }
        }' \
        localhost:8006/api/api-signature-selector

The response contains the plugin invocation details for the specified natural language query:

.. code-block:: json

    {
      "run_completed": true,
      "final_text_response": null,
      "detected_plugin_operations": [
        {
          "plugin": {
            "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping.json",
            "schema_version": "v1",
            "name": "Klarna Shopping",
            "description": "Assistant uses the Klarna plugin to get relevant product suggestions for any shopping or product discovery purpose.",
            "openapi_doc_url": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
            "auth": {
              "type": "none",
              "authorization_type": null,
              "verification_tokens": null,
              "scope": null,
              "client_url": null,
              "authorization_url": null,
              "authorization_content_type": null,
              "token_validation_url": null
            },
            "logo_url": "https://www.klarna.com/assets/sites/5/2020/04/27143923/klarna-K-150x150.jpg",
            "contact_email": "openai-products@klarna.com",
            "legal_info_url": "https://www.klarna.com/us/legal/",
            "api_endpoints": [
              "https://www.klarna.com/us/shopping/public/openai/v0/products"
            ],
            "plugin_operations": {
              "/public/openai/v0/products": {
                "get": {
                  "human_usage_examples": [
                    "Show me some T Shirts.",
                    "Show me some pants.",
                    "Show me winter jackets for men."
                  ],
                  "prompt_signature_helpers": [],
                  "plugin_cleanup_helpers": [
                    "Use markdown",
                    "Summarize and list the products"
                  ]
                }
              }
            }
          },
          "api_called": "https://www.klarna.com/us/shopping/public/openai/v0/products",
          "method": "get",
          "mapped_operation_parameters": {
            "countryCode": "US",
            "q": "tshirt",
            "size": "4"
          }
        }
      ],
      "response_time": 3.09,
      "tokens_used": 367,
      "llm_api_cost": 0.0
    }


The output shows the selected plugin, the specific operation to call and how to call it, including any applicable parameter values to be passed by the calling system.


OpenPlugin API Details
======================

You can further explore the request and response JSON structures of the two API server operations by opening http://localhost:8006/api/docs on your local API server. A corresponding OpenAPI spec can be retrieved from http://localhost:8006/api/openapi.json.