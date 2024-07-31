=================
URL to HTML
=================

The URL to HTML Processor is a processor that fetches HTML content from a specified URL. It is a crucial component for web scraping tasks, allowing applications to retrieve and process web page content.

**Supported Input Port:**

httpurl: The URL to HTML Processor accepts input through the "httpurl" port. The input should be a string representing the URL from which the HTML content needs to be fetched.

**Supported Output Port:**

html: The processor produces output through the "html" port. The output is the HTML content of the fetched web page.

List of Implementations:
===========================

Request Implementation
----------------------------

The Request implementation of the URL to HTML Processor uses the Request library to send HTTP requests and fetch HTML content.

**Metadata**


Sample processor configuration:
----------------------------------

NOTE: Processor is always added to a module(Input or Output). The module is then added to the pipeline.


.. code-block:: json

     {
        "processor_type": "url_to_html",
        "processor_implementation_type": "url_to_html_with_request",
        "input_port": "httpurl",
        "output_port": "html",
        "metadata": {},
    }
