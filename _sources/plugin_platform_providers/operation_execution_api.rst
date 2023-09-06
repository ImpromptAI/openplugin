==================================
Operation Execution API
==================================

Request
==========

The API endpoint: {{SERVER_ENDPOINT}}/api/operation-execution

.. tabs::

  .. tab:: curl

    .. code-block:: sh

      curl -X POST \
        -H 'x-api-key: your-api-key' \
        -H 'Content-Type: application/json' \
        -d '{
                "api": "https://www.klarna.com/us/shopping/public/openai/v0/products",
                "method": "get",
                "query_params": {
                    "countryCode": "US",
                    "q": "tshirt",
                    "size": 4
                },
                "header": {
                    "x-api-token":"abcd"
                },
                "post_processing_cleanup_prompt": "Write a summary of the response."
            }' \
        https://api.imprompt.ai/openplugin/api/operation-execution

  .. tab:: python

    .. code-block:: python

        import requests
        import json

        url = "https://api.imprompt.ai/openplugin/api/operation-execution"

        payload = json.dumps({
            "api": "https://www.klarna.com/us/shopping/public/openai/v0/products",
            "method": "get",
            "query_params": {
                "countryCode": "US",
                "q": "tshirt",
                "size": 4
            },
            "header": {
                "x-api-token":"abcd"
            },
            "post_processing_cleanup_prompt": "Write a summary of the response."
        })
        headers = {
          'Content-Type': 'application/json',
          'x-api-key': 'your-api-key'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)


  .. tab:: REST

    .. code-block:: sh

        API Endpoint: https://api.imprompt.ai/openplugin/api/operation-execution

        Method: POST

        Headers: {
          'x-api-key': 'your-api-key'
          'Content-Type': 'application/json'
        }

        Body: {
            "api": "https://www.klarna.com/us/shopping/public/openai/v0/products",
            "method": "get",
            "query_params": {
                "countryCode": "US",
                "q": "tshirt",
                "size": 4
            },
            "header": {
                "x-api-token":"abcd"
            },
            "post_processing_cleanup_prompt": "Write a summary of the response."
        }

Response
============

.. code-block:: json

    {
        "response": {
            "products": [
                {
                    "name": "Maison MM6 Margiela Tshirt",
                    "url": "https://www.klarna.com/us/shopping/pl/cl10001/3202504255/Clothing/Maison-MM6-Margiela-Tshirt/?utm_source=openai&ref-site=openai_plugin",
                    "price": "$42.96",
                    "attributes": [
                        "Material:Cotton",
                        "Target Group:Woman",
                        "Color:Black",
                        "Size (Small-Large):S,XL,XS,L,M"
                    ]
                },
                {
                    "name": "Nasa Worm Logotype TShirt",
                    "url": "https://www.klarna.com/us/shopping/pl/cl10001/3201822232/Clothing/Nasa-Worm-Logotype-TShirt/?utm_source=openai&ref-site=openai_plugin",
                    "price": "$14.99",
                    "attributes": [
                        "Material:Cotton",
                        "Target Group:Man",
                        "Color:Red",
                        "Size (Small-Large):S,XL,XS,L,M,XXL"
                    ]
                },
                {
                    "name": "Antigua Inter Miami CF Vivid Polo TShirt M",
                    "url": "https://www.klarna.com/us/shopping/pl/cl491/3202133394/Sports-Fan-Apparel/Antigua-Inter-Miami-CF-Vivid-Polo-TShirt-M/?utm_source=openai&ref-site=openai_plugin",
                    "price": "$53.99",
                    "attributes": [
                        "Target Group:Man",
                        "Sport:Soccer",
                        "Size (Small-Large):S,XL,3XL,L,M,XXL",
                        "Team:Inter Miami CF"
                    ]
                },
                {
                    "name": "Puma Women's Classics TShirt Dress",
                    "url": "https://www.klarna.com/us/shopping/pl/cl10001/3202065101/Clothing/Puma-Women-s-Classics-TShirt-Dress/?utm_source=openai&ref-site=openai_plugin",
                    "price": "$10.00",
                    "attributes": [
                        "Material:Cotton",
                        "Target Group:Woman",
                        "Color:White,Black",
                        "Size (Small-Large):S,XL,XS,L,M"
                    ]
                }
            ]
        },
        "post_cleanup_text": "The response includes a list of four products. \n\n1. The Maison MM6 Margiela T-shirt is available for $42.96. It is made of cotton and is targeted towards women. It comes in black and is available in sizes S, XL, XS, L, and M. The product can be found [here](https://www.klarna.com/us/shopping/pl/cl10001/3202504255/Clothing/Maison-MM6-Margiela-Tshirt/?utm_source=openai&ref-site=openai_plugin).\n\n2. The Nasa Worm Logotype T-Shirt is priced at $14.99. It is made of cotton and is targeted towards men. It comes in red and is available in sizes S, XL, XS, L, M, and XXL. The product can be found [here](https://www.klarna.com/us/shopping/pl/cl10001/3201822232/Clothing/Nasa-Worm-Logotype-TShirt/?utm_source=openai&ref-site=openai_plugin).\n\n3. The Antigua Inter Miami CF Vivid Polo T-Shirt M is priced at $53.99. It is targeted towards men and is specifically designed for soccer fans who support the Inter Miami CF team. It is available in sizes S, XL, 3XL, L, M, and XXL. The product can be found [here](https://www.klarna.com/us/shopping/pl/cl491/3202133394/Sports-Fan-Apparel/Antigua-Inter-Miami-CF-Vivid-Polo-TShirt-M/?utm_source=openai&ref-site=openai_plugin).\n\n4. The Puma Women's Classics T-Shirt Dress is available for $10.00. It is made of cotton and is targeted towards women. It comes in white and black and is available in sizes S, XL, XS, L, and M. The product can be found [here](https://www.klarna.com/us/shopping/pl/cl10001/3202065101/Clothing/Puma-Women-s-Classics-TShirt-Dress/?utm_source=openai&ref-site=openai_plugin)."
    }

API Body Parameters
===================
These parameters are used to configure the API request. The API request body is a JSON object with the following fields:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - api
     - string
     - The API endpoint to be used for the API call.
   * - method
     - string
     - The HTTP method to be used for the API call.
   * - query_params
     - object
     - The query parameters to be used for the API call.
   * - header
     - object
     - The header parameters to be used for the API call.
   * - post_processing_cleanup_prompt
     - string
     - The prompt to be used for post-processing the API response.
   * - llm
     - object
     - The configurations for the LLM (Large Language Model) provider.

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
        **Available options include:** OpenAIChat
     - *Required
   * - model_name
     - string
     - .. line-block::
        The name of the LLM model.
        **Available options include:**
        For OpenAIChat, model_name="gpt-3.5-turbo, gpt-3.5-turbo-0613, gpt-4-0613, gpt-4"
     - *Required
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
