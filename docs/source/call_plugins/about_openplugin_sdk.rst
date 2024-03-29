========================================
About Openplugin SDK
========================================


The OpenPlugin SDK for python is a powerful and versatile toolkit designed to streamline the integration and consumption of OpenPlugin API services. This SDK empowers developers to effortlessly leverage the capabilities of the OpenPlugin ecosystem, promoting rapid development.

https://github.com/ImpromptAI/openplugin-sdk

Openplugin SDK supports two functions:


**1. Select a Plugin**

This function facilitates the selection of a suitable plugin from an array of installed plugins, according to the user's prompt.


.. code-block:: python
    
    from openplugin_sdk import OpenpluginService
    from openplugin_sdk import get_output_module_names
    from openplugin_sdk import UserAuthHeader, Approach, LLM, Config
    
    openplugin_server_endpoint = "..."
    openplugin_api_key = "..."
    svc = OpenpluginService(
        openplugin_server_endpoint=openplugin_server_endpoint,
        openplugin_api_key=openplugin_api_key,
    )
    openplugin_manifest_url = (
        "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping2.json"
    )
    prompt = "Show me some T Shirts."
    openplugin_manifest_urls = [openplugin_manifest_url]
    config = Config(openai_api_key="...")
    response = svc.select_a_plugin(
        openplugin_manifest_urls=openplugin_manifest_urls,
        prompt=prompt,
        config=config,
    )
    print(response)

**2. Run a Plugin**

After a plugin has been selected, the "Run a Plugin" function enables the execution of the plugin. 

.. code-block:: python
    
    from openplugin_sdk import OpenpluginService
    
    openplugin_server_endpoint = "..."
    openplugin_api_key = "..."
    svc = OpenpluginService(
        openplugin_server_endpoint=openplugin_server_endpoint,
        openplugin_api_key=openplugin_api_key,
    )
    openplugin_manifest_url = (
        "https://assistant-management-data.s3.amazonaws.com/Klarna_Shopping2.json"
    )
    prompt = "Show me some T Shirts."
    output_module_name = "default_cleanup_response"
    response = svc.run(
        openplugin_manifest_url=openplugin_manifest_url,
        prompt=prompt,
        output_module_names=[output_module_name],
    )
    print(response)