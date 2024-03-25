========================================
Call Plugins
========================================

.. toctree::
    :titlesonly:

    ../_notebooks/simple_demo
    ../_notebooks/user_auth_demo
    ../_notebooks/advanced_demo



Quickstart
-----------------------------------------

NOTE: Learn more about openplugin-sdk at: https://github.com/ImpromptAI/openplugin-sdk

.. code-block:: python

  pip install openplugin-sdk
  remote_server_endpoint = "...."
  openplugin_api_key = "...."
  svc = OpenpluginService(
          remote_server_endpoint=remote_server_endpoint, api_key=openplugin_api_key
  )

  openplugin_manifest_url = "...."
  prompt = "..."
  output_module_name="..."

  response = svc.run(
          openplugin_manifest_url=openplugin_manifest_url,
          prompt=prompt,
          output_module_names=[output_module_name],
  )
  print(f"Response={response.value}")
