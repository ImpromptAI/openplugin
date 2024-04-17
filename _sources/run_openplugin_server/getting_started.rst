.. _host-plugins-getting-started:


========================================
Getting Started
========================================


You can run your own OpenPlugin server, or use public instances that are already hosted in the cloud. 


Setup Environment Variables
------------------------------------

The OpenPlugin server supports multiple function calling LLM models. To enable support for the desired function-calling models on your server, it is necessary to provide the API Key for each model. This is accomplished through the use of environment variables.

Note: Make sure to replace ``<YOUR KEY>`` with your API key.

Note: You only need to set the keys for the models you intend to use. For example, if you only intend to use OpenAI's ChatGPT, you only need to set the ``OPENAI_API_KEY`` variable.


The content of your ``.env`` file based on provider should be as follows:

.. tabs::

  .. tab:: OpenAI

    .. code-block:: sh

      OPENAI_API_KEY=<YOUR KEY>

      DEFAULT_PROVIDER_NAME=openai
      DEFAULT_MODEL_NAME=gpt-3.5-turbo-0125
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: Anthropic

    .. code-block:: sh

      ANTHROPIC_API_KEY=<YOUR KEY>

      DEFAULT_PROVIDER_NAME=anthropic
      DEFAULT_MODEL_NAME=claude-3-sonnet-20240229
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: Google

    .. code-block:: sh

      GOOGLE_API_KEY=<YOUR KEY>

      DEFAULT_PROVIDER_NAME=google
      DEFAULT_MODEL_NAME=gemini-pro
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: Cohere

    .. code-block:: sh

      COHERE_API_KEY=<YOUR KEY>

      DEFAULT_PROVIDER_NAME=cohere
      DEFAULT_MODEL_NAME=command-r
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: FireworksAI

    .. code-block:: sh

      FIREWORKS_API_KEY=<YOUR KEY>

      DEFAULT_PROVIDER_NAME=fireworks
      DEFAULT_MODEL_NAME=accounts/fireworks/models/firefunction-v1
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: MistralAI
      
    .. code-block:: sh
  
      MISTRAL_API_KEY=<YOUR KEY>
      DEFAULT_PROVIDER_NAME=mistralai
      DEFAULT_MODEL_NAME=mistral-large-latest
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1

  .. tab:: Custom
      
    .. code-block:: sh
  
      #TODO: Not supported yet
      CUSTOM_AUTH_TYPE='api_key'
      CUSTOM_ENDPOINT=''
      CUSTOM_API_KEY=''
      
      DEFAULT_PROVIDER_NAME=openai
      DEFAULT_MODEL_NAME='gpt-4'
      DEFAULT_TEMPERATURE=0
      DEFAULT_TOP_P=0.1
      DEFAULT_N=1


There are different ways to start the OpenPlugin API server.

NOTE: OpenPlugin is built with the python version 3.9.

Start the OpenPlugin server using python library from PyPI
-----------------------------------------------------------------

.. code-block:: bash
  
  pip install openplugin
  openplugin --help
  openplugin start-server /path/to/your/.env


Start the OpenPlugin server from code using poetry
-----------------------------------------------------------------

.. code-block:: bash

  git clone https://github.com/ImpromptAI/openplugin
  cd openplugin
  # install poetry in the machine
  poetry install
  # add .env file with the required API keys
  poetry run python start_api_server.py

NOTE: The ``start_api_server.py`` script reads the ``.env`` file to setup the keys.

Start the OpenPlugin server using docker
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


API Hosted by Imprompt
---------------------------------

Hosted API Spec: https://api.imprompt.ai/prod/openplugin/api/openapi.json

NOTE: Host your own instance of the service or you’ll need to get a key from jeffrschneider[at]gmail[dot]com to access the hosted service.