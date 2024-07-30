.. image:: /_images/openplugin_hero_header.png
   :alt: leapix
   :class: leapix-logo

========================================
Language Enabled API eXtensions
========================================

Extensions are added to the OpenAPI document to provide additional information for OpenPlugin to improve the success of tools used by the LLM.

Here are the details about the extensions OpenPlugin supports.

Extensions
=============

x-openplugin
------------------------
OpenPlugin is an extension to hold metadata such as marketplace data, contact information, test document urls, etc.

Example:

.. code-block:: json

    "x-openplugin": {
        "name": "My First Plugin",
        "description": "This my very first plugin!",
        "contactEmail": "barrett@imprompt.ai",
        "logoUrl": "https://example.com/logo.png",
        "legalInfoUrl": "https://example.com/terms-of-service",
        "permutateDocUrl": "https://openplugin.s3.amazonaws.com/a94899b116cd4d47b697414006f0852a/permutate/b/permutate.json"
        "schemaVersion": "0.0.1",
    }

.. note::
  The schema version is a string that denotes the version of OpenPlugin, indicating its feature set capabilities. It follows the ``major.minor.patch`` format for versioning.


x-plugin-auth
------------------------
Plugin auth contains information to with the plugin for operation calls. Accompaning data for the appropriate authentication type (oauth, bearer, basic, etc.) is included in the extension.

.. note::
  Plugin authentication is exclusively managed through this extension in OpenPlugin. Consequently, it does not rely on the OpenAPI security object.

**1. No Auth:**

The plugin does not require any authentication and can be used by any user without providing any authentication.

Example:

.. code-block:: json

    "x-plugin-auth": {
        "type": "none"
    }

**2. OAuth:**

The plugin uses OAuth to authenticate with the user's account. The plugin will redirect the user to the OAuth provider's login page and then redirect the user back to the plugin with an access token.

Example:

.. code-block:: json

    "x-plugin-auth": {
        "type": "oauth"
        "clientUrl": "https://accounts.google.com/o/oauth2/auth",
        "authorizationUrl": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/drive.file",
        "authorizationContentType": "application/x-www-form-urlencoded",
        "tokenValidationUrl": "https://www.googleapis.com/oauth2/v1/tokeninfo",
    }

**3. User Level:**

This authentication type requires users to provide their own API key to the plugin. The plugin developer can provide a user level API key to Imprompt when the plugin is installed. Imprompt will use the user level API key to authenticate with the plugin.

Example:

.. code-block:: json

   "x-plugin-auth": {
      "type": "user_http",
      "authorizationType": "bearer",
    }


**4. Service Level:**

The plugin developer can provide a service level API key to Imprompt when the plugin is registered. Imprompt will use the service level API key to authenticate with the plugin.


Example:

.. code-block:: json

    "x-plugin-auth": {
      "type": "service_http",
      "authorizationType": "bearer"
    }


x-human-usage-examples
------------------------
Human usage examples illustrate how a person might utilize a specific operation. These examples provide valuable insights and practical suggestions, helping users better understand how to effectively interact with the operation.


x-helpers
------------------------
Helpers is an extention that contains useful information for the LLM to understand the operation or parameters within an operation. This can include information such a descriptions, suggested values, and hints at both an operation and parameter level.

.. code-block:: json

  "parameters": [
    {
      "name": "q",
      "in": "query",
      "required": true,
      "schema": {
        "type": "string"
      },
      "x-helpers": [
        "The search term to find products",
      ]
    }
  ]


x-bootstrap
------------------------
The bootstrap flag indicates that an operation is a bootstrap operation. This is useful for bringing broadly applicable data into the session when the plugin is used. For instance, if other plugin operations require a user or organization ID, bootstrapping the operation to obtain this ID can be beneficial. The data provided by the bootstrap operation will be included in the LLM context window.

.. note::
  Bootstrap operations must have their parameters provided through the x-bootstrap-value extension. This is necessary because bootstrap operations do not rely on the LLM to construct the call. Therefore, all required parameters must have values explicitly provided.

  You may access auth token or auth response values as seen in these examples:
  - {{ auth.token }}
  - {{ auth.data.access_token }} // auth.data is the response object
  - {{ auth.data.user_id }}


.. code-block:: json

  "/oauth/v1/access-tokens/{token}": {
      "get": {
          "operationId": "get-/oauth/v1/access-tokens/{token}_get",
          "parameters": [
              {
                  "name": "token",
                  "in": "path",
                  "required": true,
                  "style": "simple",
                  "explode": false,
                  "schema": {
                      "type": "string"
                  },
                  "x-bootstrap-value": "{{ auth.data.access_token }}"
              }
          ],
          "responses": {
              "200": {
                  "description": "successful operation",
                  "content": {
                      "application/json": {
                          "schema": {
                              "$ref": "#/components/schemas/AccessTokenInfoResponse"
                          }
                      }
                  }
              },
              "default": {
                  "$ref": "#/components/responses/Error"
              }
          },
          "x-bootstrap": true,
      }
  }


x-filter
------------------------
The filter refines an operation's response by extracting only the most meaningful data. This process is beneficial for reducing the size of the context window and preventing irrelevant information from being displayed or interpreted by the language model.

Example:

.. code-block:: json

  "responses": {
      "200": {
          "description": "Products found",
          "content": {
              "application/json": {
                  "schema": {
                      "$ref": "#/components/schemas/ProductResponse"
                  }
              }
          },
          "x-filter": {
              "description": "Filter the response",
              "finish_output_port": "json",
              "initial_input_port": "json",
              "name": "Filter the response",
              "processors": [
                  {
                      "input_port": "json",
                      "output_port": "json",
                      "metadata": {
                          "template": "{\n    \"products\": [\n        {% for product in products %}\n        {\n            \"name\": \"{{ product.name }}\",\n            \"price\": \"{{ product.price }}\",\n            \"url\": \"{{ product.url }}\"\n        }\n        {% if not loop.last %},{% endif %}\n        {% endfor %}2\n    ]\n}",
                          "mime_type": "application/json"
                      },
                      "processor_implementation_type": "template_engine_with_jinja",
                      "processor_type": "template_engine"
                  }
              ]
          }
      },
  },


x-dependent
------------------------
Operations often include parameters that rely on the results of other operations to determine their values (e.g., an ID). This extension is used to trigger the plugin to call the dependent operation in order to ascertain the value of the parameter.

Example:

.. code-block:: json

  "parameters": [
      {
          "name": "origin_city_id",
          "in": "query",
          "description": "The id of the origin city",
          "required": true,
          "schema": {
              "type": "string"
          },
          "x-dependent": {
              "path": "/api/v1/find_city_id",
              "method": "get",
          }
      }
  ]


x-lookup
------------------------
This extension is similar to x-dependent, but is used on the operation response to help resolve fields that may not be human readable. This is useful for the LLM to understand the value of a field that may be an id or a code.

Example:

.. code-block:: json

  "x-lookup": {
    "path": "/api/v1/train_providers",
    "method": "get",
    "parameter": "$request.query.train_provider_id"
  }

.. notes::
  The parameter field follows JSON Schema notation. It is used to map the value from the response attribute, where the x-lookup is attached, to the parameter in the lookup request.


x-output-modules
------------------------
Output modules enable plugin developers to transform an operation's response into a desirable format for the user. These modules can perform tasks such as summarizing a JSON response into natural language or generating visually appealing UI displays using JSX or Jinja templating.

Example:

.. code-block:: json

  "x-output-modules": [
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


x-few-shot-examples
------------------------
Few-shot examples enable plugin developers to define prompts and parameter slot filling for specific operations. By providing these examples, developers can inform the LLM, thereby enhancing its accuracy and understanding of the operation.

The prompt and parameter_mapping are two key elements within the x-few-shot-example.

Prompt
~~~~~~~~~~~~~~~~~~~~~~~~
The prompt is a string that represents a natural language question or command that a user might ask. It is designed to trigger the specific operation that the example is attached to. The prompt should be written in a way that it clearly indicates the intent of the operation.

Parameter Mapping
~~~~~~~~~~~~~~~~~~~~~~~~
The parameter mapping is a dictionary that associates the parameters in the prompt with their corresponding request parameter values. This helps the AI understand how parts of the user's input align with the parameters defined in the API.

Example:

.. code-block:: json

  "x-few-shot-examples": [
    {
      "prompt": "Find the id for Austin.",
      "parameter_mapping": {
        "city": "Austin"
      }
    },
    {
      "prompt": "What is the identifier for the city known as Buenos Aires?",
      "parameter_mapping": {
        "city": "Buenos Aires"
      }
    }
  ]
