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


Start an OpenPlugin implementation server
=========================================


1. With Python
----------------


To install using pip, run:

.. code-block:: shell

    pip install openplugin


You can verify you have OpenPlugin installed by running:

.. code-block:: shell

    openplugin --help


To start the OpenPlugin implementation server, run:

.. code-block:: shell

    openplugin start-server



2. With Docker
----------------
Passing environment variables in the startup script:

.. code-block:: shell

    docker run --name [container-name] -p 8012:8012 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest


If you want to pass environment variables as a file, you can create a .env file:

.. code-block:: shell

    nano [env-filename]


Include the following variables as necessary:

.. code-block:: shell

    OPENAI_API_KEY=[your_key]
    COHERE_API_KEY=[your_key]
    GOOGLE_APPLICATION_CREDENTIALS=[your_key]


Then run the following command:

.. code-block:: shell

    docker run --name [container-name] -p 8012:8012 --env-file [path-to-env-file] -d shrikant14/openplugin:latest


API Hosted by Imprompt
=========================================

Hosted API Spec: https://api.imprompt.ai/openplugin/api/openapi.json

Hosted Swagger Docs: https://api.imprompt.ai/openplugin/api/docs

**NOTE:**  Host your own instance of the service or you’ll need to get a key from jeffrschneider[at]gmail[dot]com to access the hosted service.
