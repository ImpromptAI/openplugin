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
            "plugin_cleanup_helpers": [],
            "prompt_signature_helpers": []
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



Plugin Cleanup Helpers
------------------------

Plugin cleanup helpers are used to change the response of an API operation. If the plugin requires the response to be in a specific format, the plugin developer can provide a plugin cleanup helper to change the response of the API operation.

**Example:** For File Manager Plugin, the plugin cleanup helpers are:

1. summarize the json response

.. note::
    The response of this plugin call will be the summary text of the json response instead of the json response.

Sample OpenPlugin Manifest
============================


.. tabs::

  .. tab:: YAML

    .. code-block:: yaml

        schema_version: 1
        name: File Manager
        description: Plugin to manage text file and content
        openapi_doc_url: https://ws.imprompt.ai/api/plugin/file-manager/openapi.json
        auth:
          type: none
        logo_url: https://imprompt-app-assets.s3.amazonaws.com/file_manager.jpg
        contact_email: shrikant@brandops.io
        legal_info_url: TODO
        plugin_operations:
          "/api/plugin/file-manager/save-in-s3-file":
            post:
              human_usage_examples:
                - Save text to s3
                - Save my article to the cloud
                - Save this stuff to a file
              prompt_signature_helpers:
                - If the content of the file is unclear, say "I'm sorry, I do not know what to put into the file."
                - If a file title is not provided, use a very short synopsis of the content
                - If any error occurs, write an apologetic message to the user
              plugin_cleanup_helpers:
                - summarize the json response
          "/api/plugin/file-manager/delete-s3-file":
            post:
              human_usage_examples:
                - Delete my article from the cloud
                - Delete this file
              prompt_signature_helpers:
                - If the file is not specified, say "I'm sorry, I do not know which file to delete."
                - If any error occurs, write an apologetic message to the user
              plugin_cleanup_helpers:
                - summarize the json response

  .. tab:: JSON

    .. code-block:: python

      {
        "schema_version": "1",
        "name": "File Manager",
        "description": "Plugin to manage text file and content",
        "openapi_doc_url": "https://ws.imprompt.ai/api/plugin/file-manager/openapi.json",
        "auth": {
            "type": "none"
        },
        "logo_url": "https://imprompt-plugin-assets.s3.amazonaws.com/system_plugins/google_gmail_icon.png",
        "contact_email": "shrikant@brandops.io",
        "legal_info_url": "TODO",
        "plugin_operations": {
            "/api/plugin/file-manager/save-in-s3-file": {
                "post": {
                    "human_usage_examples": [
                        "Save text to s3",
                        "Save my article to the cloud",
                        "Save this stuff to a file"
                    ],
                    "prompt_signature_helpers": [
                        "If the content of the file is unclear, say I'm sorry, I do not know what to put into the file.",
                        "If a file title is not provided, use a very short synopsis of the content",
                        "If any error occurs, write an apologetic message to the user"
                    ],
                    "plugin_cleanup_helpers": [
                        "summarize the json response
                    ]
                }
            },
            "/api/plugin/file-manager/delete-s3-file": {
                "post": {
                    "human_usage_examples": [
                        "Delete my article from the cloud",
                        "Delete this file"
                    ],
                    "prompt_signature_helpers": [
                        "If the file is not specified, say I'm sorry, I do not know which file to delete."
                        "If any error occurs, write an apologetic message to the user"
                    ],
                    "plugin_cleanup_helpers": [
                        "summarize the json response
                    ]
                }
            }
        }
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
     - integer
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
   * - plugin_operations
     - object
     - This contains the operations defined in the OpenAPI document and extends to include useful examples and helpers for the model.


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
   * - plugin_cleanup_helpers
     - array
     - Helper prompt to clean up the response of the plugin.

