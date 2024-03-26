.. _host-plugins-getting-started:


========================================
Getting Started
========================================


You can run your own OpenPlugin servers, or use public instances that are already hosted in the cloud. 

The OpenPlugin server is capable of supporting multiple LLM models for processing. To enable support for all desired models on your server, it is necessary to provide the API Key for each model. This is accomplished through the use of environment variables.

The content of your ``.env`` file should be as follows:

.. code-block:: text

    OPENAI_API_KEY=<YOUR KEY>
    COHERE_API_KEY=<YOUR KEY
    AZURE_API_KEY=<YOUR KEY>
    GOOGLE_API_KEY=<YOUR KEY>
    AWS_ACCESS_KEY=<YOUR KEY>
    AWS_SECRET_KEY=<YOUR KEY

Make sure to replace ``<YOUR KEY>`` with your API key.

**Note:** You only need to set the keys for the models you intend to use. For example, if you only intend to use OpenAI's ChatGPT, you only need to set the ``OPENAI_API_KEY`` variable.

**NOTE:** You can also pass LLM API keys as a POST parameter when you call run_plugin API on the OpenPlugin server. The server will use the API key passed in the request to make the API call to the LLM model.


There are different ways to start the OpenPlugin API server.

**Start the OpenPlugin server using python library from PyPI**
-----------------------------------------------------------------

.. code-block:: bash
  
  pip install openplugin
  openplugin --help
  export OPENAI_API_KEY=<your key>
  openplugin start-server


**Start the OpenPlugin server from code using poetry**
-----------------------------------------------------------------

.. code-block:: bash

  git clone https://github.com/ImpromptAI/openplugin
  cd openplugin
  # install poetry in the machine
  poetry install
  # add .env file with the required API keys
  poetry run python start_api_server.py

NOTE: The ``start_api_server.py`` script reads the ``.env`` file to setup the keys.

**Start the OpenPlugin server using docker**
-----------------------------------------------------------------

.. code-block:: bash

  # Passing environment variables in the startup script
  docker run --name openplugin_container -p 8006:8006 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest
  

  # Passing environment variables as a file
  nano [env-filename]
  Add to file
    [variable1-name]=[value1]
    [variable2-name]=[value2]
    [variable3-name]=[value3]
  docker run --name openplugin_container -p 8006:8006 --env-file my_env.env -d shrikant14/openplugin:latest


**API Hosted by Imprompt**
---------------------------------

Hosted API Spec: https://api.imprompt.ai/openplugin/api/openapi.json

Hosted Swagger Docs: https://api.imprompt.ai/openplugin/api/docs

NOTE: Host your own instance of the service or you’ll need to get a key from jeffrschneider[at]gmail[dot]com to access the hosted service.