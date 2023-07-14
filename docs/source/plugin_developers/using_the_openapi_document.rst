==========================
Using the OpenAPI Document
==========================

The Manifest File has a link to the `OpenAPI document <https://swagger.io/specification>`_ that describes your API.

If you have a large API with many operations, we suggest you create a small OpenAPI file with only the APIs you want to expose in your plugin.

We expect these fields to be present in the OpenAPI document: Info, Servers, Tags, Paths and Components.

Sample OpenAPI document: https://www.klarna.com/us/shopping/public/openai/v0/api-docs/

Auto-Generate
-------------

We provide a utility to generate the OpenAPI document from the project level OpenAPI document. See: :ref:`openplugin-manifest-file`
