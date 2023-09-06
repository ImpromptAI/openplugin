==================================
Plugin Selector API
==================================

The API endpoint: {{SERVER_ENDPOINT}}/api/plugin-selector

Request
=========

.. tabs::

  .. tab:: curl

    .. code-block:: sh

      curl -X POST \
        -H 'x-api-key: your-api-key' \
        -H 'Content-Type: application/json' \
        -d '{
          "messages": [{
              "content":"Show me 5 t shirts?",
              "message_type":"HumanMessage"
          }],
          "tool_selector_config": {
              "provider":"OpenAI",
              "pipeline_name":"default"
          },
          "plugins": [{
              "manifest_url":"https://www.klarna.com/.well-known/ai-plugin.json"
          }],
          "config": {},
          "llm": {
              "provider":"OpenAIChat",
              "model_name":"gpt-3.5-turbo-0613"
          }
      }' \
        https://api.imprompt.ai/openplugin/api/plugin-selector

  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "https://api.imprompt.ai/openplugin/api/plugin-selector"

        payload = json.dumps({
          "messages": [
            {
              "content": "Show me 4 tshirts",
              "message_type": "HumanMessage"
            }
          ],
          "tool_selector_config": {
            "provider": "OpenAI",
            "pipeline_name": "default"
          },
          "plugins": [
            {
              "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Open_AI_Klarna_product_Api.json"
            }
          ],
          "config": {},
          "llm": {
            "provider": "OpenAIChat",
            "model_name": "gpt-3.5-turbo-0613"
          }
        })
        headers = {
          'x-api-key': 'your-api-key',
          'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


  .. tab:: REST

    .. code-block:: sh

        API Endpoint: https://api.imprompt.ai/openplugin/api/plugin-selector

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
            "messages": [{
                "content":"Show me 5 t shirts?",
                "message_type":"HumanMessage"
            }],
            "tool_selector_config": {
                "provider":"OpenAI",
                "pipeline_name":"default"
            },
            "plugins": [{
                "manifest_url":"https://www.klarna.com/.well-known/ai-plugin.json"
            }],
            "config": {},
            "llm": {
                "provider":"OpenAIChat",
                "model_name":"gpt-3.5-turbo-0613"
            }
        }


Response
==========

.. code-block:: json

    {
        "run_completed": true,
        "final_text_response": null,
        "detected_plugin_operations": [
            {
                "plugin": {
                    "manifest_url": "https://assistant-management-data.s3.amazonaws.com/Open_AI_Klarna_product_Api.json",
                    "schema_version": "1",
                    "name": "Open AI Klarna product Api",
                    "description": "TODO",
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
                    "logo_url": "TODO",
                    "contact_email": "TODO",
                    "legal_info_url": "TODO",
                    "api_endpoints": [
                        "https://www.klarna.com/us/shopping/public/openai/v0/products"
                    ],
                    "plugin_operations": {
                        "/public/v0/products": {
                            "get": {
                                "human_usage_examples": [
                                    "I want to buy mens athletic t-shirts ",
                                    "Do you have tennis shoes?"
                                ],
                                "prompt_signature_helpers": []
                            }
                        }
                    }
                },
                "api_called": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                "method": "get"
            }
        ],
        "response_time": 2.86,
        "tokens_used": 411,
        "llm_api_cost": 0.0
    }


API Body Parameters
===================
These parameters are used to configure the API request. The API request body is a JSON object with the following fields:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - messages
     - array
     - The list of messages to be processed by the LLM. This will include your plugin prompt as well as any context messages.
   * - tool_selector_config
     - object
     - The configurations for the tool selector, such as the provider and pipeline name.
   * - plugins
     - array
     - The list of plugins to evaluate for tool selection.
   * - config
     - object
     - The API configurations applicable for the plugins.
   * - llm
     - object
     - The configurations for the LLM (Large Language Model) provider.


Messages
--------
Messages is an array of objects. Each object represents a message to be processed by the LLM. It has the following fields:

.. list-table::
   :widths: 15 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - content
     - string
     - The content of the message.
   * - message_type
     - string
     - .. line-block::
        The type of the message.
        **Available options include:** HumanMessage, AIMessage, SystemMessage, FunctionMessage.


Tool Selector Config
--------------------
The tool selector config object represents the configurations for the tool selector. It has the following fields:

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - provider
     - string
     - .. line-block::
        The provider for the Tool Selector.
        **Available options include:** Imprompt, OpenAI, Langchain.
   * - pipeline_name
     - string
     - .. line-block::
        The name of the pipeline for the Tool Selector.
        **Available options include:**
        For OpenAI, pipeline_name=default;
        For Langchain, pipeline_name="zero-shot-react-description, react-docstore, conversational-react-description";
        For Imprompt, pipeline_name=default


1. **Imprompt:** Imprompt is a tool selector that uses a custom prompt with LLM to select the best tool for the given message.

2. **OpenAI:** OpenAI is a tool selector that uses OpenAI functions to select the best tool for the given prompt messages.

3. **Langchain:** Langchain is a tool selector that uses Langchain Agent to select the best tool for the given message.


Plugins
-------
Plugins is an array of objects. Each object represents a plugin to be evaluated by the tool selector. It has the following fields:

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - manifest_url
     - string
     - The URL of the plugin manifest. The plugin manifest should be OpenPlugin compliant.


Config
------
It has the following fields:

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - openai_api_key
     - string
     - The OpenAI API key. Required, if you are using the OpenAI tool selector.
   * - cohere_api_key
     - string
     - The Cohere API key. Required, if you are using the Cohere tool selector.


LLM
---
This contains the configurations for an LLM (Large Language Model) provider.

.. list-table::
   :widths: 20 15 55 15
   :header-rows: 1

   * - Field
     - Type
     - Description
     - Default
   * - provider
     - LLMProvider
     - .. line-block::
        The provider for the LLM.
        **Available options include:** OpenAI, OpenAIChat, GooglePalm, Cohere.
     - *Required
   * - model_name
     - string
     - .. line-block::
        The name of the LLM model.
        **Available options include:**
        For OpenAI, model_name="text-davinci-003"
        For OpenAIChat, model_name="gpt-3.5-turbo, gpt-3.5-turbo-0613, gpt-4-0613, gpt-4"
        For GooglePalm, model_name="chat-bison@001, text-bison-001"
        For Cohere, model_name="command, command-light, command-xlarge-nightly"
     - *Required
   * - temperature
     - number
     - The temperature parameter for generating output.
     - 0.7
   * - max_tokens
     - integer
     - The maximum number of tokens in the generated output.
     - 1024
   * - top_p
     - number
     - The top-p parameter for generating output.
     - 1
   * - frequency_penalty
     - number
     - The frequency penalty for generating output.
     - 0
   * - presence_penalty
     - number
     - The presence penalty for generating output.
     - 0
   * - n
     - number
     - The n parameter for generating output.
     - 1
   * - best_of
     - number
     - The best-of parameter for generating output.
     - 1
   * - max_retries
     - integer
     - The maximum number of retries for generating output.
     - 6
