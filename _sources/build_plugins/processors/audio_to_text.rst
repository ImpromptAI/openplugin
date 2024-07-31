=================
Audio To Text
=================

The Audio to Text Processor is a component in the OpenPlugin system that converts audio input into textual output. It plays a crucial role in extracting spoken words from audio files and transforming them into written text.

**Supported Input Port**

audio: The Audio to Text Processor accepts input through the "audio" port. The input should be an audio file or a reference to an audio file.

**Supported Output Port**

text: The processor produces output through the "text" port. The output is a string representing the transcribed text extracted from the audio input.


List of Implementations
============================

Whisper Implementation
-------------------------

The Whisper implementation of the Audio to Text Processor utilizes OpenAI's Whisper model to convert audio to text. Whisper is a state-of-the-art speech recognition model that can accurately transcribe spoken words from audio files.


**Metadata**

.. list-table::
   :widths: 15 20 55
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - openai_api_key
     - string (required)
     - The API key for accessing OpenAI's Whisper ASR system. This key is user-provided.
   * - model_name
     - string (optional)
     - The name of the model to be used for the audio to text conversion. The default value is "whisper-1".


Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.

.. code-block:: json

     {
        "processor_type": "file_to_text",
        "processor_implementation_type": "file_to_text_with_langchain",
        "input_port": "filepath",
        "output_port": "text",
        "metadata": {},
    }
