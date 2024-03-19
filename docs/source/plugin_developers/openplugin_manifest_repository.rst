=================================
OpenPlugin Manifest Repository
=================================


1. openplugin-manifests (for vendors)
------------------------------------------------

Repository Link: (https://github.com/ImpromptAI/openplugin-manifests)

This repository is dedicated to the storage of plugin assets specifically for our vendors. It comprises two distinct folders. The first folder contains official plugins, which are constructed and maintained by the vendors themselves. The second folder houses unofficial plugins, developed by independent developers who do not own the API, but are interested in creating plugins for certain vendors.

**How can I contribute?**

You are welcome to create a fork of this repository and subsequently generate a pull request featuring your plugin assets. Upon receipt of your pull request, our team will conduct a thorough review. Following approval, your plugin will be accessible to all users of Openplugin and Imprompt.

Please note: To publish your plugin in the official directory, it is essential to verify your ownership of the associated APIs.

#COMING_SOON: Steps to prove the ownership of the APIs.

**How can I use these plugins?**

There are two ways to use these plugins:

1. All plugins are accessible in the Imprompt marketplace. To use them, simply sign up at https://www.imprompt.ai and select the plugins you wish to use.

2. You can build and start the OpenPlugin server and use the OpenPlugin-SDK to access these plugins.

#COMING_SOON: redirect to do these steps.


2. openplugin-community (samples for developers)
------------------------------------------------

Repository Link: (https://github.com/ImpromptAI/openplugin-community)

This repository is dedicated to the storage of plugin assets for testing purposes. We have added few sample plugins for the developers to understand the structure of the plugin and how to create a plugin.  


Use cases:
--------------


1. I don't want to create a plugin but I want to test a plugin.
-----------------------------------------------------------------

Let's say you want to test our unofficial klarna plugin. You can follow the below steps:

**Step 1:** Sample Klarna plugin manifest=https://raw.githubusercontent.com/ImpromptAI/openplugin-manifests/main/vendor-owned/unofficial/klarna/manifest.json

**Step 2:** Start the openplugin server or get the openplugin server url from us.

**Step 3:** Install the openplugin-sdk

.. code-block:: bash

    pip install openplugin-sdk

**Step 4:** Run the plugin

.. code-block:: python

    # setup openplugin service with remote server url
    from openplugin_sdk import OpenpluginService
    import os

    openplugin_server_endpoint = "..."
    openplugin_api_key = "..."

    svc = OpenpluginService(openplugin_server_endpoint=openplugin_server_endpoint, openplugin_api_key=openplugin_api_key)
    print(f"openplugin_version: {svc.remote_server_version()}, server_status={svc.ping()}")
    openplugin_manifest_url = "https://raw.githubusercontent.com/ImpromptAI/openplugin-manifests/main/vendor-owned/unofficial/klarna/manifest.json"
    prompt = "Show me some T Shirts."
    output_module_name = "default_cleanup_response"

    response = svc.run(
            openplugin_manifest_url=openplugin_manifest_url,
            prompt=prompt,
            output_module_names=[output_module_name],
    )
    print(response.value)


2. I have an openapi specification url and I want to create a plugin for it.
-------------------------------------------------------------------------------

You can follow the below steps:


**Step 1:** Fork the openplugin-manifests repository.

**Step 2:** If you are the owner of this API then create a new folder in the vendor-owned/official folder with the name of your plugin. If you are not the owner of this API then create a new folder in the vendor-owned/unofficial folder.

**Step 3:** Create a new file `<plugin_name>_manifest.json` in the folder created in step 2. Make sure your manifest file has the `openapi_doc_url` key with the value as the link to your openapi specification.

**Step 4:** Test your plugin with openplugin.

**Step 5:** If you want to add this plugin to openplugin-manifests repo then create a pull request.


3. I have an API and I want to create a plugin for it.
------------------------------------------------------------

Do all of the above steps and then follow the below steps:

**Step:** Create a new file `<plugin_name>_openapi.json` in your plugin folder.

NOTE: Make sure your manifest file has the `openapi_doc_url` key with the value as the link to your openapi specification.

