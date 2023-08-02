.. _openplugin-manifest:

===================
OpenPlugin Manifest
===================

The OpenPlugin Manifest is a YAML/JSON file that contains information about the plugin. It is used to both discover the plugin in a marketplace, as well as links information on how to run the plugin.

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


OpenPlugin Manifest
======================

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
     - Helpers for the interaction and response of the model with the operation.
   * - plugin_cleanup_helpers
     - array
     - Helper prompt to clean up the response of the plugin.

