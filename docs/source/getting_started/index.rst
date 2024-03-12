=================
Getting Started
=================

Table of Contents
-----------------

.. contents::
   :local:
   :depth: 2


Start the OpenPlugin server
===============================
You can run your own OpenPlugin servers, or use public instances that are already hosted in the cloud. 

The OpenPlugin server is capable of supporting multiple LLM models for processing. To enable support for all desired models on your server, it is necessary to provide the API Key for each model. This is accomplished through the use of environment variables.

The content of your ``.env`` file should be as follows:

.. code-block:: text

    OPENAI_API_KEY=<YOUR KEY>
    COHERE_API_KEY=<YOUR KEY
    AZURE_API_KEY=<YOUR KEY>
    GOOGLE_API_KEY=<YOUR KEY>
    AWS_ACCESS_KEY=<YOUR KEY>
    AWS_SECRET_KEY=<YOUR KEY

Make sure to replace ``<YOUR KEY>`` with your API key.

**Note:** You only need to set the keys for the models you intend to use. For example, if you only intend to use OpenAI's ChatGPT, you only need to set the ``OPENAI_API_KEY`` variable.

**NOTE:** You can also pass LLM API keys as a POST parameter when you call run_plugin API on the OpenPlugin server. The server will use the API key passed in the request to make the API call to the LLM model.


There are different ways to start the OpenPlugin API server.

**1: Start the OpenPlugin server using python library from PyPI**

.. code-block:: bash
  
  pip install openplugin
  openplugin --help
  export OPENAI_API_KEY=<your key>
  openplugin start-server


**2: Start the OpenPlugin server from code using poetry**

.. code-block:: bash

  git clone https://github.com/ImpromptAI/openplugin
  cd openplugin
  # install poetry in the machine
  poetry install
  # add .env file with the required API keys
  poetry run python start_api_server.py

NOTE: The ``start_api_server.py`` script reads the ``.env`` file to setup the keys.

**3: Start the OpenPlugin server using docker**

.. code-block:: bash

  # Passing environment variables in the startup script
  docker run --name openplugin_container -p 8006:8006 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest
  

  # Passing environment variables as a file
  nano [env-filename]
  Add to file
    [variable1-name]=[value1]
    [variable2-name]=[value2]
    [variable3-name]=[value3]
  docker run --name openplugin_container -p 8006:8006 --env-file my_env.env -d shrikant14/openplugin:latest


Build A Plugin
===================

We will create a demo plugin for Klarna, a comparison shopping service. An official Klarna LLM plugin is available for OpenAI's ChatGPT, but our Klarna plugin will be usable with any LLM via OpenPlugin.

As with ChatGPT plugins, OpenPlugin consumes a manifest describing the operations available in the API of the service. The manifest contains a reference to the API specification in OpenAPI (Swagger) format along with natural language annotations for each operation, making each operation as clear to the LLM as possible.

Here is the complete OpenPlugin manifest for our Klarna plugin:

.. code-block:: json

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

The details of the manifest format are defined in :ref:`openplugin-manifest`. For our purposes, note the ``plugin_operations`` property in the above JSON: it specifies the API operation used in the following steps. Save the manifest and make it available to your OpenPlugin API server for retrieval via HTTP/S.


Run a plugin
===============================


**1. Run an openplugin using PyPI**

.. code-block:: bash

  pip install openplugin
  openplugin --help
  export OPENAI_API_KEY=<your key>
  openplugin start-servero
  openplugin run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"


**2. Run an openplugin using server API**

.. code-block:: text
  
    curl --location 'https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline' \
           --header 'Content-Type: application/json' \
           --header 'x-api-key: 'YOUR-API-KEY' \
           --data '{
            "prompt": "USER_PROMPT",
            "conversation": [],
            "openplugin_manifest_url": "MANIFEST_URL",
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
              "pre_prompt": null
            },
            "output_module_names":["default_cleanup_response"]
            }'


**3. Run an openplugin using code**

.. code-block:: python

  pip install openplugin
  from openplugin.core.plugin_runner import run_prompt_on_plugin
  openplugin=""
  prompt=""
  response =await run_prompt_on_plugin(openplugin, prompt)

  
**4. Run an openplugin using openplugin-sdk**

NOTE: Learn more about openplugin-sdk at: https://github.com/ImpromptAI/openplugin-sdk

.. code-block:: python

  pip install openplugin-sdk
  remote_server_endpoint = "...."
  openplugin_api_key = "...."
  svc = OpenpluginService(
          remote_server_endpoint=remote_server_endpoint, api_key=openplugin_api_key
  )

  openplugin_manifest_url = "...."
  prompt = "..."
  output_module_name="..."

  response = svc.run(
          openplugin_manifest_url=openplugin_manifest_url,
          prompt=prompt,
          output_module_names=[output_module_name],
  )
  print(f"Response={response.value}")
