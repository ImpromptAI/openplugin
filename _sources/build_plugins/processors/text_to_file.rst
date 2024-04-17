=================
Text to File
=================

The Text to File Processor is a processor that saves input text to a file. It plays a crucial role in storing and persisting text data, enabling applications to save generated or processed text for future use or reference.

**Supported Input Port:**

text: The Text to File Processor accepts input through the "text" port. The input should be a string representing the text that needs to be saved to a file.

**Supported Output Port:**

filepath: The processor produces output through the "filepath" port. The output is the file path of the generated file containing the saved text.

List of Implementations:
===========================

Default Implementation
----------------------------

The Default implementation of the Text to File Processor saves the input text to a file using the specified configuration options.

**Metadata**

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - file_type
     - string (optional)
     - The type of the file to which the text will be saved. The default value is "txt".
   * - file_name
     - string (optional)
     - The name of the output file. The default value is "response".
   * - folder_name
     - string (optional)
     - The folder where the generated text file will be stored. The default value is "assets".

Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "text_to_file",
        "processor_implementation_type": "text_to_file_with_default",
        "input_port": "text",
        "output_port": "filepath",
        "metadata": {},
    }
