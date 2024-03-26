.. _build-plugins-getting-started:

========================================
Getting Started
========================================

A plugin is a yaml/json file that encapsulates various properties about your plugin. The OpenPlugin manifest contains a reference to the OPENAPI specification. This format is widely used for designing and building APIs in a standardized manner.

To learn about all plugin manifest properties, refer to this guide: :ref:`openplugin-manifest`


Sample Klarna Plugin
==============================

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



Use cases:
--------------


I have an openapi specification url and I want to create a plugin for it.
-------------------------------------------------------------------------------

You can follow the below steps:

**Step 1:** Fork the openplugin-manifests repository.

**Step 2:** If you are the owner of this API then create a new folder in the vendor-owned/official folder with the name of your plugin. If you are not the owner of this API then create a new folder in the vendor-owned/unofficial folder.

**Step 3:** Create a new folder with the name 'openplugin_manifest' in the folder created in step 2.

**Step 3:** Create a new file `<plugin_name>_manifest.json` in the folder created in step 3. Make sure your manifest file has the `openapi_doc_url` key with the value as the link to your openapi specification.

**Step 4:** Test your plugin with openplugin server.

**Step 5:** If you want to add this plugin to openplugin-manifests repo then create a pull request.


I have an API and I want to create a plugin for it.
------------------------------------------------------------

Do all of the above steps and then follow the below steps:

**Step:** Create a new file `<plugin_name>_openapi.json` in your plugin folder.

NOTE: Make sure your manifest file has the `openapi_doc_url` key with the value as the link to your openapi specification.


