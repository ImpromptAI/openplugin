=================
HTML to Text
=================

HTML to Text Processor is a processor that converts HTML input into text output. It is primarily used for extracting text content from HTML, which can be useful in various applications like web scraping, content extraction, and more.

**Supported Input Port:**

html: The HTML to Text Processor accepts input through the "html" port. The input should be a string representing the HTML that needs to be converted to text.

**Supported Output Port:**

text: The processor produces output through the "text" port. The output is the plain text extracted from the input HTML.

List of Implementations:
===========================

BeautifulSoup Implementation
----------------------------

The BeautifulSoup implementation of the HTML to Text Processor uses the BeautifulSoup library to parse the HTML and extract the text content.

**Metadata**

Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "html_to_text",
        "processor_implementation_type": "html_to_text_with_bs",
        "input_port": "html",
        "output_port": "text",
        "metadata": {},
    }
