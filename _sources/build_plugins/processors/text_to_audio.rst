=================
Text to Audio
=================


Text to Audio Processor is a processor that converts text input into audio output. It plays a crucial role in transforming written text into spoken words, enabling applications to generate audio content dynamically.

**Supported Input Port:**

text: The Text to Audio Processor accepts input through the "text" port. The input should be a string representing the text that needs to be converted to audio.

**Supported Output Port:**

filepath: The processor produces output through the "filepath" port. The output is the file path of the generated audio file.

List of Implementations:
===========================

Azure Implementation
----------------------------

The Azure implementation of the Text to Audio Processor utilizes Azure's text-to-speech capabilities to convert text to audio.


**Metadata**

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - voice_name
     - string (optional)
     - The name of the voice to be used for the audio output. The default value is "en-US-AriaNeural".
   * - azure_region
     - string (optional)
     - The Azure region where the text-to-speech service is located. The default value is "eastus".
   * - azure_api_key
     - string (required)
     - The API key for accessing Azure's text-to-speech service. This key is user-provided.
   * - output_filename
     - string (optional)
     - The name of the output audio file. The default value is "output.mp3". 
   * - output_folder
     - string (optional)
     - The folder where the generated audio file will be stored. The default value is "assets".


Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "text_to_audio",
        "processor_implementation_type": "text_to_audio_with_azure",
        "input_port": "text",
        "output_port": "filepath",
        "metadata": {},
    }


