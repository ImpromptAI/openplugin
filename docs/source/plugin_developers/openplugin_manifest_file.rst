==================================
OpenPlugin Manifest File
==================================


Openplugin Manifest contains information about the plugin and the links to the OpenAPI doc and Operation details file.

We have a utility function/API to generate the OpenPlugin Manfiest File from scratch, using the OpenAPI document or from the existing OpenAI Manifest file.
:ref:`openplugin-files-creation`


Sample Openplugin Manifest(In progress)

.. code-block:: yaml

    schema_version: v1
    name: Klarna Shopping
    description: Search and compare prices from thousands of online shops. Only
      available in the US.
    openapi_doc_url: https://www.klarna.com/us/shopping/public/openai/v0/api-docs/
    llm_operation_details: https://www.klarna.com/us/shopping/public/openai/v0/api-docs/
    auth:
      type: none
    logo_url: https://www.klarna.com/assets/sites/5/2020/04/27143923/klarna-K-150x150.jpg
    contact_email: openai-products@klarna.com
    legal_info_url: https://www.klarna.com/us/legal/


OpenAPI Spec Document
=======================

Every manifest file should have a link to the OpenAPI document.

If you have a project level OpenAPI document containing 100s of APIs/Operations, then we suggest you to create a new OpenAPI file with only the APIs you want to expose as a plugin.

As LLM has token limitations, we suggest you to keep only the plugin related information in the OpenAPI document.

We expect these fields to be present in the OpenAPI document.

1. info
2. servers
3. tags
4. paths
5. components

Sample OpenAPI document: https://www.klarna.com/us/shopping/public/openai/v0/api-docs/


We have a utility function/API to generate the OpenAPI document from the project level OpenAPI document.
:ref:`openplugin-files-creation`

