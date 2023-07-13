==================================
API Usage
==================================

Hosted API Spec: https://api.imprompt.ai/openplugin/api/openapi.json

Hosted Swagger Docs: https://api.imprompt.ai/openplugin/api/docs

**NOTE:**  To use the hosted service, host your own instance of the service or you’ll need to get a key from jeffrschneider[at]gmail[dot]com

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
        https://api.imprompt.ai/openplugin/api/run-plugin

  .. tab:: python

    .. code-block:: python

      import requests

      response = requests.post(
          "https://api.imprompt.ai/openplugin/api/run-plugin",
          headers={
              "x-api-key": "your-api-key",
              "Content-Type": "application/json"
          },
          json={
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
      )

      print(response.json())

  .. tab:: REST

    .. code-block:: sh

        API Endpoint: https://api.imprompt.ai/openplugin/api/run-plugin

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




**API Body Parameters:** Represents the request body for running the plugin.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - messages
     - Array of Message
     - The list of messages to be processed.
   * - tool_selector_config
     - ToolSelectorConfig
     - The configuration for the tool selector.
   * - plugins
     - Array of Plugin
     - The list of plugins to be executed.
   * - config
     - Config
     - The API configuration for the plugin.
   * - llm
     - LLM
     - The configuration for the LLM (Language Model) provider.


**Message:** Represents a prompt to be executed.

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
     - MessageType
     - The type of the message.

**MessageType** = [HumanMessage, AIMessage, SystemMessage, FunctionMessage]


**ToolSelectorConfig**: Represents the configuration for a Tool Selector.

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - provider
     - ToolSelectorProvider
     - The provider for the Tool Selector.
   * - pipeline_name
     - string
     - The name of the pipeline for the Tool Selector.

An enumeration for different Tool Selector providers= [ Langchain, Imprompt, OpenAI]

1. OpenAI: OpenAI is a tool selector that uses OpenAI functions to select the best tool for the given prompt messages.

2. Langchain: Langchain is a tool selector that uses Langchain Agent to select the best tool for the given message.

3. Imprompt: Imprompt is a tool selector that uses a custom prompt with LLM to select the best tool for the given message.


**Plugin:** Represents a plugin configuration.

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - schema_version
     - string
     - The version of the plugin schema.
   * - name_for_model
     - string
     - The name of the plugin for the model.
   * - name_for_human
     - string
     - The name of the plugin for human reference.
   * - description_for_model
     - string
     - The description of the plugin for the model.
   * - description_for_human
     - string
     - The description of the plugin for human reference.
   * - logo_url
     - string
     - The URL of the plugin's logo.
   * - contact_email
     - string
     - The contact email for the plugin.
   * - legal_info_url
     - string
     - The URL for legal information about the plugin.
   * - manifest_url
     - string
     - The URL of the plugin manifest.
   * - api
     - PluginAPI
     - The API configuration for the plugin.


**PluginAPI:** Represents the API configuration for a plugin.

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - type
     - string
     - The type of the API.
   * - url
     - string
     - The URL of the API.
   * - has_user_authentication
     - boolean
     - Indicates if the API requires user authentication.
   * - api_endpoints
     - array of string
     - The list of API endpoints provided by the plugin.

**Config:** Represents the API configuration for a plugin.

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - openai_api_key
     - string
     - The OpenAI API key.

**LLM:** Represents the configuration for an LLM (Language Model) provider.

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - provider
     - LLMProvider
     - The provider for the LLM.
   * - model_name
     - string
     - The name of the LLM model.
   * - temperature
     - number
     - The temperature parameter for generating output.
   * - max_tokens
     - integer
     - The maximum number of tokens in the generated output.
   * - top_p
     - number
     - The top-p parameter for generating output.
   * - frequency_penalty
     - number
     - The frequency penalty for generating output.
   * - presence_penalty
     - number
     - The presence penalty for generating output.
   * - n
     - number
     - The n parameter for generating output.
   * - best_of
     - number
     - The best-of parameter for generating output.
   * - max_retries
     - integer
     - The maximum number of retries for generating output.
**LLMProvider**

An enumeration for different LLM providers. [OpenAI, OpenAIChat, GooglePalm, Cohere]