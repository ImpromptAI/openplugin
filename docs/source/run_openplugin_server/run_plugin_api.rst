==================================
Run Plugin API
==================================

Request
==========

The API endpoint: {{SERVER_ENDPOINT}}/api/plugin-execution-pipeline

.. tabs::

  .. tab:: curl

    .. code-block:: text

        curl --location 'https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline' \
           --header 'Content-Type: application/json' \
           --header 'x-api-key: 'YOUR-API-KEY' \
           --data '{
            "prompt": "Show me some T Shirts.",
            "conversation": [],
            "openplugin_manifest_url": "manifests/sample_klarna.json",
            "header":{},
            "config":{},
            "approach": {
              "base_strategy": "oai functions",
              "llm": {
                "frequency_penalty": 0,
                "max_tokens": 2048,
                "model_name": "gpt-3.5-turbo-0613",
                "presence_penalty": 0,
                "provider": "OpenAI",
                "temperature": 0,
                "top_p": 1
              },
              "name": "OAI functions-OpenAI",
              "pre_prompt": ""
            },
            "output_module_names":["default_cleanup_response"]
            }'
  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline"

        payload = json.dumps({
                    "prompt": "Show me some T Shirts.",
                    "conversation": [],
                    "openplugin_manifest_url": "manifests/sample_klarna.json",
                    "header":{},
                    "approach": {
                      "base_strategy": "oai functions",
                      "llm": {
                        "frequency_penalty": 0,
                        "max_tokens": 2048,
                        "model_name": "gpt-3.5-turbo-0613",
                        "presence_penalty": 0,
                        "provider": "OpenAI",
                        "temperature": 0,
                        "top_p": 1
                      },
                      "name": "OAI functions-OpenAI",
                      "pre_prompt": ""
                    },
                    "output_module_names":["default_cleanup_response","summary_response", "template_response"]
                  })
        headers = {
          'Content-Type': 'application/json',
          'x-api-key': 'your-api-key'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)


  .. tab:: REST

    .. code-block:: sh

        API Endpoint: https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
                "prompt": "Show me some T Shirts.",
                "conversation": [],
                "openplugin_manifest_url": "manifests/sample_klarna.json",
                "header":{},
                "approach": {
                  "base_strategy": "oai functions",
                  "llm": {
                    "frequency_penalty": 0,
                    "max_tokens": 2048,
                    "model_name": "gpt-3.5-turbo-0613",
                    "presence_penalty": 0,
                    "provider": "OpenAI",
                    "temperature": 0,
                    "top_p": 1
                  },
                  "name": "OAI functions-OpenAI",
                  "pre_prompt": ""
                },
                "output_module_names":["default_cleanup_response","summary_response", "template_response"]
              }

Response
============

.. code-block:: json

    {
        "metadata": {
            "start_time": "2024-03-06 15:02:52.063296",
            "end_time": "2024-03-06 15:02:55.929065",
            "total_time_taken_seconds": 3.865769,
            "total_time_taken_ms": 865769
        },
        "response": {
            "input_modules": [
                {
                    "name": "default_no_change_input",
                    "data_type": "TEXT",
                    "mime_type": null,
                    "value": "Show me some T Shirts.",
                    "metadata": {
                        "processing_time_seconds": 0,
                        "status_code": 200
                    }
                }
            ],
            "api_and_signature_detection_step": {
                "api_called": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                "method": "get",
                "metadata": {
                    "processing_time_seconds": 1.3412530422210693,
                    "tokens_used": 368,
                    "llm_api_cost": 0.0005665000000000001,
                    "status_code": 200
                },
                "mapped_operation_parameters": {
                    "q": "T Shirts",
                    "size": 5
                }
            },
            "api_execution_step": {
                "original_response": {
                    "name": "original_response",
                    "data_type": "JSON",
                    "mime_type": null,
                    "value": {
                        "products": [
                            {
                                "name": "Lacoste Men's T-shirts 3-pack - Black",
                                "url": "https://www.klarna.com/us/shopping/pl/cl10001/3202043025/Clothing/Lacoste-Men-s-T-shirts-3-pack-Black/?utm_source=openai&ref-site=openai_plugin",
                                "price": "$27.19",
                                "attributes": [
                                    "Material:Jersey,Cotton",
                                    "Target Group:Man",
                                    "Color:Black"
                                ]
                            },
                            {
                                "name": "Kenzo T Shirts",
                                "url": "https://www.klarna.com/us/shopping/pl/cl10001/3208499396/Clothing/Kenzo-T-Shirts/?utm_source=openai&ref-site=openai_plugin",
                                "price": "$89.99",
                                "attributes": [
                                    "Material:Cotton",
                                    "Target Group:Man",
                                    "Color:White"
                                ]
                            },
                            {
                                "name": "Nike Shortsleeve Crewneck T-shirts 2-pack - Black/Black",
                                "url": "https://www.klarna.com/us/shopping/pl/cl10001/3200175752/Clothing/Nike-Shortsleeve-Crewneck-T-shirts-2-pack-Black-Black/?utm_source=openai&ref-site=openai_plugin",
                                "price": "$31.87",
                                "attributes": [
                                    "Material:Elastane/Lycra/Spandex,Cotton",
                                    "Target Group:Man",
                                    "Color:Black"
                                ]
                            },
                            {
                                "name": "Diesel Diesel T-shirt con logo peekaboo T-Shirts Donna Nero Nero",
                                "url": "https://www.klarna.com/us/shopping/pl/cl10001/3212894543/Clothing/Diesel-Diesel-T-shirt-con-logo-peekaboo-T-Shirts-Donna-Nero-Nero/?utm_source=openai&ref-site=openai_plugin",
                                "price": "$99.76",
                                "attributes": [
                                    "Material:Cotton",
                                    "Color:Black"
                                ]
                            },
                            {
                                "name": "Hanes Boy's Ultimate Lightweight T-shirts 5-Pack - Assorted (BUBCR5)",
                                "url": "https://www.klarna.com/us/shopping/pl/cl359/3201157848/Children-s-Clothing/Hanes-Boy-s-Ultimate-Lightweight-T-shirts-5-Pack-Assorted-%28BUBCR5%29/?utm_source=openai&ref-site=openai_plugin",
                                "price": "$10.20",
                                "attributes": [
                                    "Color:White",
                                    "Target Group:Boy"
                                ]
                            }
                        ]
                    },
                    "metadata": {
                        "processing_time_seconds": 0.195066,
                        "status_code": 200
                    }
                },
                "clarifying_response": null
            },
            "output_module_map": {
                "default_cleanup_response": {
                    "name": "default_cleanup_response",
                    "data_type": "TEXT",
                    "mime_type": null,
                    "value": "\nName: Lacoste Men's T-shirts 3-pack - Black\nURL: https://www.klarna.com/us/shopping/pl/cl10001/3202043025/Clothing/Lacoste-Men-s-T-shirts-3-pack-Black/?utm_source=openai&ref-site=openai_plugin\nPrice: $27.19\n\n\nName: Kenzo T Shirts\nURL: https://www.klarna.com/us/shopping/pl/cl10001/3208499396/Clothing/Kenzo-T-Shirts/?utm_source=openai&ref-site=openai_plugin\nPrice: $89.99\n\n\nName: Nike Shortsleeve Crewneck T-shirts 2-pack - Black/Black\nURL: https://www.klarna.com/us/shopping/pl/cl10001/3200175752/Clothing/Nike-Shortsleeve-Crewneck-T-shirts-2-pack-Black-Black/?utm_source=openai&ref-site=openai_plugin\nPrice: $31.87\n\n\nName: Diesel Diesel T-shirt con logo peekaboo T-Shirts Donna Nero Nero\nURL: https://www.klarna.com/us/shopping/pl/cl10001/3212894543/Clothing/Diesel-Diesel-T-shirt-con-logo-peekaboo-T-Shirts-Donna-Nero-Nero/?utm_source=openai&ref-site=openai_plugin\nPrice: $99.76\n\n\nName: Hanes Boy's Ultimate Lightweight T-shirts 5-Pack - Assorted (BUBCR5)\nURL: https://www.klarna.com/us/shopping/pl/cl359/3201157848/Children-s-Clothing/Hanes-Boy-s-Ultimate-Lightweight-T-shirts-5-Pack-Assorted-%28BUBCR5%29/?utm_source=openai&ref-site=openai_plugin\nPrice: $10.20\n\n",
                    "metadata": {
                        "processing_time_seconds": 0.0059,
                        "status_code": 200
                    }
                },
                "summary_response": {
                    "name": "summary_response",
                    "data_type": "TEXT",
                    "mime_type": null,
                    "value": "The response includes a list of different clothing products for men and boys. The products range from Lacoste Men's T-shirts 3-pack in black for $27.19 to Hanes Boy's Ultimate Lightweight T-shirts 5-Pack in assorted colors for $10.20. Each product listing includes details such as the name, URL, price, material, target group, and color options. The products cater to different preferences and offer a variety of options for customers to choose from.",
                    "metadata": {
                        "processing_time_seconds": 1.8005,
                        "status_code": 200
                    }
                },
                "template_response": {
                    "name": "template_response",
                    "data_type": "TEXT",
                    "mime_type": "text/jsx",
                    "value": "<div className=\"container\">\n  <div className=\"row\">\n    {response.products.map((product, index) => (\n      <div key={index} className=\"col-md-4 mb-4\">\n        <div className=\"card h-100\">\n          <div className=\"card-header\">\n            {product.name}\n          </div>\n          <div className=\"card-body\">\n            <h5 className=\"card-title\">{product.price}</h5>\n            <a href={product.url} className=\"btn btn-primary\" target=\"_blank\" rel=\"noopener noreferrer\">Buy Now</a>\n          </div>\n        </div>\n      </div>\n    ))}\n  </div>\n</div>",
                    "metadata": {
                        "processing_time_seconds": 0.0001,
                        "status_code": 200
                    }
                }
            },
            "default_output_module": "default_cleanup_response",
            "performance_metrics": [
                {
                    "name": "input_module_step",
                    "label": "Input Module",
                    "processing_time_seconds": 0,
                    "status_code": 200
                },
                {
                    "name": "api_and_signature_detection_step",
                    "label": "Signature Creation (w/ LLM)",
                    "processing_time_seconds": 1.3412530422210693,
                    "status_code": 200
                },
                {
                    "name": "api_execution_step",
                    "label": "API Execution",
                    "processing_time_seconds": 0.195066,
                    "status_code": 200
                },
                {
                    "name": "default_cleanup_response",
                    "label": "Output Module [ default cleanup response ]",
                    "parallel": true,
                    "processing_time_seconds": 0.0059,
                    "status_code": 200
                },
                {
                    "name": "summary_response",
                    "label": "Output Module [ summary response ]",
                    "parallel": true,
                    "processing_time_seconds": 1.8005,
                    "status_code": 200
                },
                {
                    "name": "template_response",
                    "label": "Output Module [ template response ]",
                    "parallel": true,
                    "processing_time_seconds": 0.0001,
                    "status_code": 200
                }
            ]
        }
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
   * - prompt
     - string
     - Prompt to the plugin.
   * - conversation
     - array
     - The list of messages to be processed by the LLM. This will include your plugin prompt as well as any context messages.
   * - openplugin_manifest_url
     - string
     - The plugin manifest URL.
   * - header
     - object
     - The header information for the API request.
   * - approach
     - object
     - The approach configuration for the plugin.
   * - output_module_names
     - array
     - List of output module names to be executed.

Conversation
--------------
Conversation is an array of objects. Each object represents a message to be processed by the LLM. It has the following fields:

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

Header
------
It has the following fields:

.. list-table::
   :widths: 20 15 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - user-http-token
     - string
     - The API key for the plugin execution pipeline.

Approach
--------------------
The tool selector config object represents the configurations for the tool selector. It has the following fields:

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - base_strategy
     - string
     - .. line-block::
        The base_strategy to run the plugin.
        **Available options include:** "LLM Passthrough (OpenPlugin and Swagger)", "LLM Passthrough (Stuffed Swagger)", "LLM Passthrough (Bare Swagger)", "imprompt basic", "oai functions"
   * - name
     - string
     - The name of the approach.
   * - pre_prompt
     - string
     - The pre_prompt for the LLM.  
   * - llm
     - object
     - The LLM configuration for the plugin.


1. **Imprompt:** Imprompt is a tool selector that uses a custom prompt with LLM to select the best tool for the given message.

2. **OpenAI:** OpenAI is a tool selector that uses OpenAI functions to select the best tool for the given prompt messages.

3. **Langchain:** Langchain is a tool selector that uses Langchain Agent to select the best tool for the given message.


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
     - **Required**
   * - model_name
     - string
     - .. line-block::
        The name of the LLM model.
        **Available options include:**
        For OpenAI, model_name="text-davinci-003"
        For OpenAIChat, model_name="gpt-3.5-turbo, gpt-3.5-turbo-0613, gpt-4-0613, gpt-4"
        For GooglePalm, model_name="chat-bison@001, text-bison-001"
        For Cohere, model_name="command, command-light, command-xlarge-nightly"
     - **Required**
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
