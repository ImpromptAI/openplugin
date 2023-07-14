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
