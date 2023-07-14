.. _openplugin-manifest-file:

========================
OpenPlugin Manifest File
========================

The OpenPlugin Manifest File contains information about the plugin that is used to both discover the plugin in a marketplace, as well as links information on how to run the plugin.

Sample OpenPlugin Manifest

.. code-block:: yaml

    schema_version: 1
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


Auto-Generate
-------------

You can create the Manifest File by hand or generate the OpenPlugin Manfiest File from either the OpenAPI document or from an existing OpenAI Manifest file.


Create OpenPlugin Manifest File from OpenAI Manifest File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ openplugin create --manifest-file <path to manifest file> --output-file <path to output file>

Convert your project level API doc to plugin level API doc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ openplugin create --api-doc-file <path to api doc file> --output-file <path to output file>