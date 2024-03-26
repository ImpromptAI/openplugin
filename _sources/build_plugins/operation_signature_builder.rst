.. _operation-signature-builder:

============================
Operation Signature Builder
============================


The Operation Signature Builder is a crucial component in the architecture of the openplugin. Its primary role is to identify which operations or APIs to call within the plugin based on the input or the context.  This detection is crucial in maintaining the functionality and integrity of the plugin, as well as ensuring the seamless interaction with the host application.


Another significant role of the Operation Signature Builder is to map the correct API parameters. This process involves matching the input parameters of the API call using the user messages.

Interface: https://github.com/ImpromptAI/openplugin/blob/main/openplugin/core/operations/operation_signature_builder.py


We have two implementations of the Operation Signature Builder in OpenPlugin:
--------------------------------------------------------------------------------

1. **Using Function Calling**

We utilize Langchain to invoke the LLM functions within the plugin. As such, we currently only support the function calls that have been implemented in Langchain.

More details about function calling with Langchain at: https://python.langchain.com/docs/modules/model_io/chat/function_calling

Our implementation using Langchain: https://github.com/ImpromptAI/openplugin/blob/main/openplugin/core/operations/implementations/operation_signature_builder_with_langchain.py


2. **Using Prompt**   

We use prompt to detect the correct operation and generate the API call signature. The prompt takes openplugin manifest along with the user input and generates the API call signature.


Implementation: https://github.com/ImpromptAI/openplugin/blob/main/openplugin/core/operations/implementations/operation_signature_builder_with_imprompt.py

.. code-block:: bash

    plugin_operation_prompt = """
    You are an AI assistant.
    Here is a tool you can use, named {name_for_model}.

    The Plugin rules:
    1. Assistant ALWAYS asks user's input for ONLY the MANDATORY parameters BEFORE calling the API.
    2. Assistant pays attention to instructions given below.
    3. Create an HTTPS API url that represents this query.
    4. Use this format: <HTTP VERB> <URL>
        - An example: GET https://api.example.com/v1/products
    5. Remove any starting periods and new lines.
    6. Do not structure as a sentence.
    7. Never use https://api.example.com/ in the API.

    {pre_prompt}

    The openapi spec file = {openapi_spec}

    The instructions are: {prompt}
    """  # noqa: E501


How to configure the Operation Signature Builder in Openplugin Manifest:
----------------------------------------------------------------------------

You can setup approach object in the openplugin manifest file to configure the Operation Signature Builder. The approach object contains the following fields:

Sample 1

.. code-block:: json

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

Sample 2:

.. code-block:: json
      
    "approach": {
        "base_strategy": "oai functions",
        "llm": {
        "frequency_penalty": 0,
        "max_tokens": 2048,
        "model_name": "accounts/fireworks/models/firefunction-v1",
        "presence_penalty": 0,
        "provider": "Fireworks",
        "temperature": 0,
        "top_p": 1
        },
        "name": "OAI functions-OpenAI",
        "pre_prompt": null
    }

Approach
--------------------
The tool selector config object represents the configurations for the tool selector. It has the following fields:

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - base_strategy
     - string
     - .. line-block::
        The base_strategy to run the plugin.
        **Available options include:** "LLM Passthrough (OpenPlugin and Swagger)", "LLM Passthrough (Stuffed Swagger)", "LLM Passthrough (Bare Swagger)", "imprompt basic", "oai functions"
   * - name
     - string
     - The name of the approach.
   * - pre_prompt
     - string
     - The pre_prompt for the LLM.  
   * - llm
     - object
     - The LLM configuration for the plugin.


LLM
---
This contains the configurations for an LLM (Large Language Model) provider.

.. list-table::
   :widths: 20 15 55 15
   :header-rows: 1

   * - Field
     - Type
     - Description
     - Default
   * - provider
     - LLMProvider
     - .. line-block::
        The provider for the LLM.
        **Available options include:** OpenAI, OpenAIChat, GooglePalm, Cohere.
     - **Required**
   * - model_name
     - string
     - .. line-block::
        The name of the LLM model.
        **Available options include:**
        For OpenAI, model_name="text-davinci-003"
        For OpenAIChat, model_name="gpt-3.5-turbo, gpt-3.5-turbo-0613, gpt-4-0613, gpt-4"
        For GooglePalm, model_name="chat-bison@001, text-bison-001"
        For Cohere, model_name="command, command-light, command-xlarge-nightly"
     - **Required**
   * - temperature
     - number
     - The temperature parameter for generating output.
     - 0.7
   * - max_tokens
     - integer
     - The maximum number of tokens in the generated output.
     - 1024
   * - top_p
     - number
     - The top-p parameter for generating output.
     - 1
   * - frequency_penalty
     - number
     - The frequency penalty for generating output.
     - 0
   * - presence_penalty
     - number
     - The presence penalty for generating output.
     - 0
   * - n
     - number
     - The n parameter for generating output.
     - 1
   * - best_of
     - number
     - The best-of parameter for generating output.
     - 1
   * - max_retries
     - integer
     - The maximum number of retries for generating output.
     - 6

