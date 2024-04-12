=================
Modules
=================

In the OpenPlugin system, modules are integral components that play a crucial role in transforming data from one format to another. 

Each module, be it an input or output module, comprises a chain of processors. These processors perform specific data transformations, ensuring that the data is in the correct format at each stage of the processing pipeline. This chain of processors within each module allows for efficient and effective data transformation in the OpenPlugin system.

NOTE: The data flow in the OpenPlugin system is such that data from input modules is fed into the plugin operation pipeline. Once this data is processed, it is then fed into the output modules.

These modules can be categorized into two types: Input Modules and Output Modules.

**Input Modules**

Input modules handle the initial processing of incoming data. They are responsible for converting the data from its original format into a format that can be processed further by subsequent processors in the pipeline. This conversion is essential as it ensures that the data is in a suitable format for the next stages of processing.

**Output Modules**

Output modules, on the other hand, handle data that has been processed by the plugin operation pipeline. They take this processed data and transform it into a format that can be used for the desired output or further processing.


Sample Input Module:
------------------------

This input module object is added at the root of the openplugin manifest. It contains a list of input modules that can be used by the plugin. The input module is selected explicitly by plugin user or implicitly by plugin execution pipeline based on user input.

.. code-block:: json

    "input_modules": [
        {
            "description": "This will handle file coming to the plugin",
            "finish_output_port": "text",
            "id": "1",
            "initial_input_port": "filepath",
            "name": "convert_file_to_text",
            "processors": [
                {
                    "input_port": "filepath",
                    "metadata": {},
                    "output_port": "text",
                    "processor_implementation_type": "file_to_text_with_langchain",
                    "processor_type": "file_to_text"
                }
            ]
        }
    ],


Sample Output Module:
-------------------------

The output module object can be added at the plugin operation level or manifest root level. It contains a list of output modules that can be used by the plugin. The output module is selected explicitly by plugin user or plugin execution pipeline uses the default output module.

.. code-block:: json

    "output_modules": [
                    {
                        "default_module": true,
                        "description": "This will convert to template response",
                        "finish_output_port": "text",
                        "initial_input_port": "json",
                        "name": "template_response",
                        "processors": [
                            {
                                "input_port": "json",
                                "metadata": {
                                    "mime_type": "text",
                                    "template": "{% for item in news_results %}\nposition= {{ item.position }}, title= {{ item.title }}, link= {{ item.link }}, snippet= {{ item.snippet }}, source= {{ item.source }}, date= {{ item.date }}\n{% endfor %}"
                                },
                                "output_port": "text",
                                "processor_implementation_type": "template_engine_with_jinja",
                                "processor_type": "template_engine"
                            }
                        ]
                    }
                ],