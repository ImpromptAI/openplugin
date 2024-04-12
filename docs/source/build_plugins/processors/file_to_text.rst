=================
File To Text
=================

File to Text Processor is a processor that converts the contents of a file into plain text. It enables applications to extract textual data from various file formats, making it accessible for further processing or analysis.

**Supported Input Port:**

filepath: The File to Text Processor accepts input through the "filepath" port. The input should be a string representing the file path of the file to be converted to text.

**Supported Output Port:**

text: The processor produces output through the "text" port. The output is a string containing the extracted text from the input file.

List of Implementations:
===========================

Langchain Implementation
----------------------------

The Langchain implementation of the File to Text Processor utilizes the Langchain library to convert files to text.

**Metadata**

Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "file_to_text",
        "processor_implementation_type": "file_to_text_with_s3",
        "input_port": "filepath",
        "output_port": "filepath",
        "metadata": {},
    }
