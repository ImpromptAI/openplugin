========================================
OpenAPI Extensions for LLMs
========================================

Extensions are added to the OpenAPI document to provide additional information for OpenPlugin to improve the success of tools used by the LLM. Below you can fix details on the extensions that are supported by OpenPlugin.

Extensions
=============

x-openplugin
------------------------
This extension contains metadata for OpenPlugin. x-openplugin includes fields such as marketplace data, contact information, test document urls, etc.

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

x-plugin-auth
------------------------
This extension contains information to with the plugin for operation calls. Accompaning data for the appropriate authentication type (oauth, bearer, basic, etc.) is included in the extension.

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
Human usage examples are examples of how a human would use the operation. This is useful for the LLM to understand user's intent in natural language as well as inform users with suggestions for how to use the operation.


x-helpers
------------------------
This extension contains useful information for the LLM to understand the operation or parameters within an operation. This can include information such a descriptions, suggested values, and hints at both an operation and parameter level.

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
Bootstrap is a flag to indicate that the operation is a bootstrap operation. This is useful for the LLM to understand that the operation is a special operation that is used to bootstrap a session when the plugin is used.

.. note::
    Bootstrap operations must have their parameters provided through the x-bootstrap-value extension. All required parameters must have a value provided.

x-filter
------------------------
This extension allows an operation response to be filtered to only the most meaningful data. This is useful to reduce the size of the context window, or to prevent irrelevant information from being displayed or interpreted by the LLM.

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
It is common for operations to include parameters that are dependent of other operations to determine their value (e.g. id). This extension is used to trigger the LLM to make a call to the dependent operation to determine the value of the parameter.

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

x-output-modules
------------------------
Output modules allow the plugin developer to transform an operation response into a desirable output for the user. Output modules satisfy tasks such as: summarize a JSON response into natural language, filter data, or return beautiful UI displays through JSX/Jinja templating.

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