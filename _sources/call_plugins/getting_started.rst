.. _call-plugins-getting-started:

========================================
Getting Started
========================================


**Call an OpenPlugin via the SDK**
------------------------------------------------

This is the preferred way to call a plugin.

Learn more about the SDK at: https://github.com/ImpromptAI/openplugin-sdk

**Step 1:** You need a link to your OpenPlugin manifest. 
For testing purposes, you can use the sample Klarna plugin manifest

https://raw.githubusercontent.com/ImpromptAI/openplugin-manifests/main/vendor-owned/unofficial/klarna/manifest.json



**Step 2:** Start an OpenPlugin server. More information :ref:`host-plugins-getting-started`


**Step 3:** Install the openplugin-sdk

.. code-block:: bash

    pip install openplugin-sdk


**Step 4:** Run the plugin

.. code-block:: python

    # Call the OpenPlugin service with a remote server url
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





**curl example **
------------------------------------------------


.. code-block:: text
  
    curl --location 'https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline' \
           --header 'Content-Type: application/json' \
           --header 'x-api-key: 'YOUR-API-KEY' \
           --data '{
            "prompt": "USER_PROMPT",
            "conversation": [],
            "openplugin_manifest_url": "MANIFEST_URL",
            "header":{},
            "approach": {
              "base_strategy": "oai functions",
              "llm": {
                "frequency_penalty": 0,
                "max_tokens": 2048,
                "model_name": "gpt-3.5-turbo-0613",
                "presence_penalty": 0,
                "provider": "OpenAI",
                "temperature": 0,
                "top_p": 1
              },
              "name": "OAI functions-OpenAI",
              "pre_prompt": null
            },
            "output_module_names":["default_cleanup_response"]
            }'


**Call an OpenPlugin using code**
------------------------------------------------

.. code-block:: python

  pip install openplugin
  from openplugin.core.plugin_runner import run_prompt_on_plugin
  openplugin=""
  prompt=""
  response =await run_prompt_on_plugin(openplugin, prompt)

  
**Call an OpenPlugin using PyPI**
------------------------------------------------

.. code-block:: bash

  pip install openplugin
  openplugin --help
  export OPENAI_API_KEY=<your key>
  openplugin start-servero
  openplugin run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"

