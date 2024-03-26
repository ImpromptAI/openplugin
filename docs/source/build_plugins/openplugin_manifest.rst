.. _openplugin-manifest:

===================
OpenPlugin Manifest
===================

The OpenPlugin Manifest is a YAML/JSON file that contains information about the plugin. It is used to both discover the plugin in a marketplace, as well as links information on how to run the plugin.

Definitions
=============

Plugin Authentication
------------------------

You can provide authentication information for your plugin in the auth section of the OpenPlugin Manifest.


Types of auth types:

**1. No Auth:**

The plugin does not require any authentication and can be used by any user without providing any authentication.

Sample:

.. code-block:: json

    "auth": {
        "type": "none"
    }

**2. OAuth:**

The plugin uses OAuth to authenticate with the user's account. The plugin will redirect the user to the OAuth provider's login page and then redirect the user back to the plugin with an access token.

Sample:

.. code-block:: json

    "auth": {
        "authorization_content_type": "application/x-www-form-urlencoded",
        "authorization_url": "https://oauth2.googleapis.com/token",
        "client_url": "https://accounts.google.com/o/oauth2/auth",
        "scope": "https://www.googleapis.com/auth/drive.file",
        "token_validation_url": "https://www.googleapis.com/oauth2/v1/tokeninfo",
        "type": "oauth"
    }

**3. User Level:**

This authentication type requires users to provide their own API key to the plugin. The plugin developer can provide a user level API key to Imprompt when the plugin is installed. Imprompt will use the user level API key to authenticate with the plugin.

Sample:

.. code-block:: json

   "auth": {
      "type": "user_http",
      "authorization_type": "bearer",
    }


**4. Service Level:**

The plugin developer can provide a service level API key to Imprompt when the plugin is registered. Imprompt will use the service level API key to authenticate with the plugin.


Sample:

.. code-block:: json

    "auth": {
      "type": "service_http",
      "authorization_type": "bearer"
    }



Plugin Operations
-------------------

Plugin operations are the operations that the plugin supports.  You can increase the accuracy of the plugin selector API by providing human usage examples, prompt signature helpers, and plugin cleanup helpers for each plugin operation.

.. note::
    The operations listed in the plugin operations object of the OpenPlugin Manifest are only used in the Plugin.

Sample:

.. code-block:: json

    "plugin_operations": {
        "/public/openai/v0/products": {
            "get": {
            "human_usage_examples": [],
            "prompt_signature_helpers": []
            "output_modules":[]
            }
        }
    }

Human Usage Examples
------------------------

Human usage examples are examples of how a human would use the plugin.

**Example:** For File Manager Plugin, the human usage examples are:

1. Save text to s3

2. Save my article to the cloud

3. Save this stuff to a file

.. note::
  They are used to improve the accuracy of the plugin selector API. The user can provide a human usage example to help the model understand the user's intent. The model will then use the human usage example to predict the plugin that the user wants to use.



Prompt Signature Helpers
------------------------

Prompt signature helpers are used to improve the accuracy of the api signature selector API. They are used to help to map the API parameters from the user's input.


**Example:** For File Manager Plugin, the prompt signature helpers are:

1. If the content of the file is unclear, say "I'm sorry, I do not know what to put into the file."

2. If a file title is not provided, use a very short synopsis of the content


.. note::
  Plugin developer can use prompt signature helpers to set default values for the API parameters.


Input Modules:
----------------

Input modules are the modules that the plugin supports. Each input module has an id, name, description, initial input port, finish output port, and processors.

.. code-block:: json
      
      [
            {
                "id": "1",
                "name": "convert_file_to_text",
                "description": "This will handle file coming to the plugin",
                "initial_input_port": "filepath",
                "finish_output_port": "text",
                "processors": [
                    {
                        "input_port": "filepath",
                        "output_port": "text",
                        "processor_type": "file_to_text",
                        "processor_implementation_type": "file_to_text_with_langchain",
                        "metadata": {}
                    }
                ]
            }
      ]

Output Modules:
----------------

Output modules are the modules that the plugin supports. Each output module has a name, description, initial input port, finish output port, and processors.

.. code-block:: json

      [
        {
            "name": "default_cleanup_response",
            "description": "This module will convert the output to text",
            "initial_input_port": "json",
            "finish_output_port": "text",
            "processors": [
                {
                    "input_port": "json",
                    "output_port": "text",
                    "processor_type": "template_engine",
                    "processor_implementation_type": "template_engine_with_jinja",
                    "metadata": {
                        "template": "{% for product in products %}\nName: {{ product['name'] }}\nURL: {{ product['url'] }}\nPrice: {{ product['price'] }}\n\n{% endfor %}"
                    }
                }
            ]
        }
      ]
  

Processor:
------------

A processor is a function that takes an input and produces an output. It is used to transform the input data into the output data.

List of supported processor types: audio_to_text

.. code-block:: json

      {
          "input_port": "json",
          "output_port": "text",
          "processor_type": "template_engine",
          "processor_implementation_type": "template_engine_with_jinja",
          "metadata": {
              "template": "{% for product in products %}\nName: {{ product['name'] }}\nURL: {{ product['url'] }}\nPrice: {{ product['price'] }}\n\n{% endfor %}"
          }
      }

NOTE: Different supported processors and implementations

#. llm_engine=llm_engine_with_openai, llm_engine_with_openai_cohere
#. text_to_audio=text_to_audio_with_azure
#. audio_to_text=audio_to_text_with_whisper
#. template_engine=template_engine_with_jinja, template_engine_with_jsx
#. text_to_file=text_to_file_with_default
#. file_to_text=file_to_text_with_langchain
#. file_to_cloud=file_to_cloud_with_s3
#. url_to_html=url_to_html_with_request
#. html_to_text=html_to_text_with_bs

Sample OpenPlugin Manifest
============================


.. tabs::

  .. tab:: YAML

    .. code-block:: yaml

        schema_version: 0.0.1
        openplugin_manifest_version: 0.0.1
        name: Klarna Shopping
        contact_email: shrikant@imprompt.ai
        description: Assistant uses the Klarna plugin to get relevant product suggestions
          for any shopping or product discovery purpose.
        openapi_doc_url: https://www.klarna.com/us/shopping/public/openai/v0/api-docs/
        legal_info_url: 
        logo_url: 
        permutate_doc_url: 
        permutation_test_urls: 
        auth:
          type: none
        input_modules:
        - id: '1'
          name: convert_file_to_text
          description: This will handle file coming to the plugin
          initial_input_port: filepath
          finish_output_port: text
          processors:
          - input_port: filepath
            output_port: text
            processor_type: file_to_text
            processor_implementation_type: file_to_text_with_langchain
            metadata: {}
        plugin_operations:
          "/public/openai/v0/products":
            get:
              human_usage_examples:
              - Show me some T Shirts.
              - Show me some pants .
              - Show me winter jackets for men.
              plugin_signature_helpers:
              - if you can't find the user's clothes size, ask the user about the size.
              - If any error occurs, write an apologetic message to the user
              output_modules:
              - name: template_response
                description: This will convert to template response
                initial_input_port: json
                finish_output_port: text
                default_module: true
                processors:
                - input_port: json
                  output_port: text
                  processor_type: template_engine
                  processor_implementation_type: template_engine_with_jsx
                  metadata:
                    pre_prompt: Get only product names, prices and urls
                    mime_type: text/jsx
                    template: |-
                      <div className="container">
                        <div className="row">
                          {response.products.map((product, index) => (
                            <div key={index} className="col-md-4 mb-4">
                              <div className="card h-100">
                                <div className="card-header">
                                  {product.name}
                                </div>
                                <div className="card-body">
                                  <h5 className="card-title">{product.price}</h5>
                                  <a href={product.url} className="btn btn-primary" target="_blank" rel="noopener noreferrer">Buy Now</a>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    template_prompt: Wrap the items in a card, using the product name in the
                      card header and the details and links in the card body. Allow for 3
                      products per row
        output_modules:
        - name: default_cleanup_response
          description: This module will convert the output to text
          initial_input_port: json
          finish_output_port: text
          processors:
          - input_port: json
            output_port: text
            processor_type: template_engine
            processor_implementation_type: template_engine_with_jinja
            metadata:
              template: |-
                {% for product in products %}
                Name: {{ product['name'] }}
                URL: {{ product['url'] }}
                Price: {{ product['price'] }}

                {% endfor %}
        preferred_approaches:
        - base_strategy: oai functions
          llm:
            frequency_penalty: 0
            max_tokens: 2048
            model_name: gpt-3.5-turbo-0613
            presence_penalty: 0
            provider: OpenAI
            temperature: 0
            top_p: 1
          name: OAI functions-OpenAI
          pre_prompt: 


  .. tab:: JSON

    .. code-block:: python

      {
          "schema_version": "0.0.1",
          "openplugin_manifest_version": "0.0.1",
          "name": "Klarna Shopping",
          "contact_email": "shrikant@imprompt.ai",
          "description": "Assistant uses the Klarna plugin to get relevant product suggestions for any shopping or product discovery purpose.",
          "openapi_doc_url": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
          "legal_info_url": null,
          "logo_url": null,
          "permutate_doc_url": null,
          "permutation_test_urls": null,
          "auth": {
              "type": "none"
          },
          "input_modules": [
              {
                  "id": "1",
                  "name": "convert_file_to_text",
                  "description": "This will handle file coming to the plugin",
                  "initial_input_port": "filepath",
                  "finish_output_port": "text",
                  "processors": [
                      {
                          "input_port": "filepath",
                          "output_port": "text",
                          "processor_type": "file_to_text",
                          "processor_implementation_type": "file_to_text_with_langchain",
                          "metadata": {}
                      }
                  ]
              }
          ],
          "plugin_operations": {
              "/public/openai/v0/products": {
                  "get": {
                      "human_usage_examples": [
                          "Show me some T Shirts.",
                          "Show me some pants .",
                          "Show me winter jackets for men."
                      ],
                      "plugin_signature_helpers": [
                          "if you can't find the user's clothes size, ask the user about the size.",
                          "If any error occurs, write an apologetic message to the user"
                      ],
                      "output_modules": [
                          {
                              "name": "template_response",
                              "description": "This will convert to template response",
                              "initial_input_port": "json",
                              "finish_output_port": "text",
                              "default_module": true,
                              "processors": [
                                  {
                                      "input_port": "json",
                                      "output_port": "text",
                                      "processor_type": "template_engine",
                                      "processor_implementation_type": "template_engine_with_jsx",
                                      "metadata": {
                                          "pre_prompt": "Get only product names, prices and urls",
                                          "mime_type": "text/jsx",
                                          "template": "<div className=\"container\">\n  <div className=\"row\">\n    {response.products.map((product, index) => (\n      <div key={index} className=\"col-md-4 mb-4\">\n        <div className=\"card h-100\">\n          <div className=\"card-header\">\n            {product.name}\n          </div>\n          <div className=\"card-body\">\n            <h5 className=\"card-title\">{product.price}</h5>\n            <a href={product.url} className=\"btn btn-primary\" target=\"_blank\" rel=\"noopener noreferrer\">Buy Now</a>\n          </div>\n        </div>\n      </div>\n    ))}\n  </div>\n</div>",
                                          "template_prompt": "Wrap the items in a card, using the product name in the card header and the details and links in the card body. Allow for 3 products per row"
                                      }
                                  }
                              ]
                          }
                      ]
                  }
              }
          },
          "output_modules": [
              {
                  "name": "default_cleanup_response",
                  "description": "This module will convert the output to text",
                  "initial_input_port": "json",
                  "finish_output_port": "text",
                  "processors": [
                      {
                          "input_port": "json",
                          "output_port": "text",
                          "processor_type": "template_engine",
                          "processor_implementation_type": "template_engine_with_jinja",
                          "metadata": {
                              "template": "{% for product in products %}\nName: {{ product['name'] }}\nURL: {{ product['url'] }}\nPrice: {{ product['price'] }}\n\n{% endfor %}"
                          }
                      }
                  ]
              }
          ],
          "preferred_approaches": [
              {
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
                  "pre_prompt": null
              }
          ]
      }



You can find more details on each of these fields below.


OpenPlugin Manifest Fields
=============================


.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - schema_version
     - string
     - The version of the OpenPlugin manifest.
   * - openplugin_manifest_version
     - string
     - The version of the OpenPlugin manifest.
   * - name
     - string
     - The name of the plugin.
   * - description
     - string
     - This description of the plugin.
   * - openapi_doc_url
     - string
     - The URL of the OpenAPI specification document of the plugin.
   * - auth
     - object
     - The authentication information for the plugin.
   * - logo_url
     - string
     - The URL of the logo for the plugin.
   * - contact_email
     - string
     - The email address of the plugin developer.
   * - legal_info_url
     - string
     - The URL of the legal information for the plugin.
   * - input_modules
     - array
     - The input modules for the plugin. Each input module has an id, name, description, initial input port, finish output port, and processors.
   * - plugin_operations
     - object
     - This contains the operations defined in the OpenAPI document and extends to include useful examples and helpers for the model.
   * - output_modules
     - array
     - The output modules for the plugin. Each output module has a name, description, initial input port, finish output port, and processors.

OpenPlugin Operations
---------------------
An OpenPlugin operation is an extension of plugin operation defined in the OpenAPI document. It is defined by a combination of a path and an HTTP method as shown in the example above. The user can attach extra details to each operation to improve LLM predictions and responses.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - human_usage_examples
     - array
     - Clear usage examples that a human can use to trigger the operation correctly.
   * - prompt_signature_helpers
     - array
     - Prompts to help fill in the parameters of the API operation from the user's input.
   * - output_modules
     - array
     - The output modules for the operation. Each output module has a name, description, initial input port, finish output port, and processors.


Input Modules:
----------------

Input modules are the modules that the plugin supports. Each input module has an id, name, description, initial input port, finish output port, and processors.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - id
     - string
     - The id of the input module.
   * - name
     - string
     - The name of the input module.
   * - description
     - string
     - The description of the input module.
   * - initial_input_port
     - string
     - The initial input port of the input module.
   * - finish_output_port
     - string
     - The finish output port of the input module.
   * - processors
     - array
     - The processors for the input module. Each processor has an input port, output port, processor type, processor implementation type, and metadata.


Output Modules:
----------------

Output modules are the modules that the plugin supports. Each output module has a name, description, initial input port, finish output port, and processors.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - name
     - string
     - The name of the output module.
   * - description
     - string
     - The description of the output module.
   * - initial_input_port
     - string
     - The initial input port of the output module.
   * - finish_output_port
     - string
     - The finish output port of the output module.
   * - processors
     - array
     - The processors for the output module. Each processor has an input port, output port, processor type, processor implementation type, and metadata.

Processor:
------------

A processor is a function that takes an input and produces an output. It is used to transform the input data into the output data.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - input_port
     - string
     - The input port of the processor.
   * - output_port
     - string
     - The output port of the processor.
   * - processor_type
     - string
     - The type of the processor.
   * - processor_implementation_type
     - string
     - The implementation type of the processor.
   * - metadata
     - object
     - The metadata for the processor.

NOTE: metadata is different for different processor types.

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

