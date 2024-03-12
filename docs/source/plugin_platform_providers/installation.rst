==================================
Installation & Execution
==================================


Setup up the environment variables
==================================
Before you run the application, be sure you have the appropriate credentials configured. You can configure them by setting environment variables as demonstrated below.

**OpenAI LLM**

.. code-block:: shell

    export OPENAI_API_KEY=<your key>

**Cohere LLM**

.. code-block:: shell

    export COHERE_API_KEY=<your key>

**Google LLM**

.. code-block:: shell

    export GOOGLE_APPLICATION_CREDENTIALS=<credential_file_path: /usr/app/application_default_credentials.json>

if you want to use a different port:

.. code-block:: shell

    export PORT=<port: 8012>


You can also setup env variables using .env file. The content of your ``.env`` file should be as follows:

.. code-block:: text

    OPENAI_API_KEY=<YOUR KEY>
    COHERE_API_KEY=<YOUR KEY
    AZURE_API_KEY=<YOUR KEY>
    GOOGLE_API_KEY=<YOUR KEY>
    AWS_ACCESS_KEY=<YOUR KEY>
    AWS_SECRET_KEY=<YOUR KEY

Make sure to replace ``<YOUR KEY>`` with your API key.

Start an OpenPlugin implementation server
=========================================

There are different ways to start the OpenPlugin API server.

**1: Start the OpenPlugin server using python library from PyPI**

.. code-block:: bash
  
  pip install openplugin
  openplugin --help
  export OPENAI_API_KEY=<your key>
  openplugin start-server


**2: Start the OpenPlugin server from code using poetry**

.. code-block:: bash

  git clone https://github.com/ImpromptAI/openplugin
  cd openplugin
  # install poetry in the machine
  poetry install
  # add .env file with the required API keys
  poetry run python start_api_server.py

NOTE: The ``start_api_server.py`` script reads the ``.env`` file to setup the keys.

**3: Start the OpenPlugin server using docker**

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
=========================================

Hosted API Spec: https://api.imprompt.ai/openplugin/api/openapi.json

Hosted Swagger Docs: https://api.imprompt.ai/openplugin/api/docs

**NOTE:**  Host your own instance of the service or you’ll need to get a key from jeffrschneider[at]gmail[dot]com to access the hosted service.
