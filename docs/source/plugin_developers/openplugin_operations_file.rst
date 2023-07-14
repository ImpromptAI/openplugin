==================================
OpenPlugin Operations File
==================================


We create a new operation details file from the OpenAPI specification document.

The user can attach extra details to each operation so that LLM can generate better predictions.

The operation details file is a YAML/JSON file that contains the following fields:

.. code-block:: yaml

    version: 1
    operations:
      "/api/plugin/file-manager/save-in-s3-file":
        post:
          extended_description: Save text to s3
          examples:
            'Save my article on LLM to s3: LLM stands for Large Language Models.':
              mapped_title: Article on LLM
              mapped_content: LLM stands for Large Language Models.
              response: "{'status': 'success'}"
              status: 200
          requestBody:
            content:
              application/json:
                schema:
                  "$ref": "#schemas/Body_create_docs_api_plugin_file_manager_save_in_s3_file_post"
    schemas:
      Body_create_docs_api_plugin_file_manager_save_in_s3_file_post:
        title: Body_create_docs_api_plugin_file_manager_save_in_s3_file_post
        type: object
        properties:
          title:
            extended_description: ''
            sample_values:
                - 'a'
                - 'b'
            examples:
                prompt:"Save my article on Generative AI"
                value: GenerativeAI
          content:
            extended_description: ''
            sample_values:
                - 'c'
                - 'd'


OpenPlugin Operations file contains following fields:


.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - version
     - string
     - The version of the operation details.
   * - openplugin_api_doc
     - string
     - The URL of the OpenAPI specification document.
   * - operations
     - object
     - The list of operations.
   * - schemas
     - object
     - The list of schemas.

You can find more details on each of these fields below.


Operation
=========
An operation is a single API call. It is defined by a combination of a path and an HTTP method as shown in the example above. It then has the following fields:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - extended_description
     - string
     - The extended description of the operation. This will help the model to understand the operation better.
   * - examples
     - object
     - The list of examples for the operation.
   * - requestBody
     - object
     - The request body for the operation.

**Example**
Represents an example.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - title
     - string
     - The title of the example.
   * - content
     - string
     - The content of the example.


**Schema**
Represents a schema.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - title
     - string
     - The title of the schema.
   * - type
     - string
     - The type of the schema.
   * - properties
     - object
     - The list of properties for the schema.


**Property**
Represents a property.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - extended_description
     - string
     - The extended description of the property.
   * - sample_values
     - array
     - The list of sample values for the property.