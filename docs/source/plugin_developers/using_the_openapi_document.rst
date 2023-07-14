===============================
Using the OpenAPI Document
===============================

Every manifest file should have a link to the `OpenAPI document <https://swagger.io/specification>`_.

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
