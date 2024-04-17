=================
Processors
=================

Processor is a component in the openplugin system that plays a crucial role in transforming and manipulating data. It is essentially a function that accepts an input, perform a specific operation or set of operations on that input, and produces an output.

**Characteristics of Processors:**

1. Processors have well-defined input and output ports. They accept input data in a specific format and produce output data in a desired format. The input and output formats can vary depending on the specific processor and its purpose.

2. The primary purpose of a processor is to transform or modify the input data in some way. This transformation can involve various operations such as filtering, aggregating, formatting, enriching, or any other custom processing logic required by the system.

3. Processors are designed to be modular and reusable components within the OpenPlugin system. They encapsulate specific functionality and can be easily integrated into different workflows or pipelines. This modularity allows for flexibility and extensibility in building complex data processing workflows.

4. Processors often have configuration options that allow customization of their behavior. 


**List of supported processors:**
-------------------------------------

.. toctree::
    :titlesonly:

    audio_to_text
    file_to_cloud
    file_to_text
    html_to_text
    llm_engine
    template_engine
    text_to_audio
    text_to_file
    url_to_html

