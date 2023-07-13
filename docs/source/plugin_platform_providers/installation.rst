==================================
Installation & Execution
==================================


Start an openplugin implementation server
==============================================================


1. With Python
================


To install using pip, run:

.. code-block:: shell

    pip install openplugin


You can verify you have openplugin installed by running:

.. code-block:: shell

    openplugin --help


To start the openplugin implementation server, run:

.. code-block:: shell

    openplugin start-server


Setup up the environment variables
=====================================
Before you run the application, be sure you have credentials configured.

if you want to use OpenAI LLM

.. code-block:: shell

    export OPENAI_API_KEY=<your key>

if you wan to use Cohere LLM

.. code-block:: shell

    export COHERE_API_KEY=<your key>

if you want to use Google LLM

.. code-block:: shell

    export GOOGLE_APPLICATION_CREDENTIALS=<credential_file_path: /usr/app/application_default_credentials.json>

if you want to use a different port

.. code-block:: shell

    export PORT=<port: 8012>



2. With Docker
================
Passing environment variables in the startup script:

.. code-block:: shell

    docker run --name [container-name] -p 8012:8012 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest

Passing environment variables as a file

.. code-block:: shell

    nano [env-filename]
    Add to file
    [variable1-name]=[value1]
    [variable2-name]=[value2]
    [variable3-name]=[value3]

    docker run --name [container-name] -p 8012:8012 --env-file my_env.env -d shrikant14/openplugin:latest``


If you want to pass environment variable as a file, you can use the following command:

.. code-block:: shell

    nano [env-filename]
    #Add your environment variables in the file
    OPENAI_API_KEY=[value1]
    COHERE_API_KEY=[value2]
    GOOGLE_APPLICATION_CREDENTIALS=[value3]

    docker run --name [container-name] -p 8012:8012 --env-file [path-to-env-file] -d shrikant14/openplugin:latest
