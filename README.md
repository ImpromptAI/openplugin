# OpenPlugin

**About**: :open_hands::electric_plug: Multimodal API Bridge - make APIs into chat and multimodal ready interfaces

Please see the complete documentation here: https://openplugin.com/

#### Summary:

This is an open source effort to create an ecosystem around LLM enabled APIs. We make it easy to "chat with an API", that is, to send natural language as the input to the API and have it process it. Then, we offer several options to easily transform the APIs response into something better suited to human consumption like text, markdown, HTML, JSX, voice, video, etc.

**Design Decisions:**
- LLM neutral (LLMs leapfrog each other in capability; swap easily, support many)
- Framework neutral (langchain, semantic kernel, ...)
- Deployment model neutral (serverless, containers, k8, ... )
- Language neutral (our manifest is declarative JSON)
- Client neutral (e.g., we're not hard coded to ChatGPT or Gemini, ...)
- Multimodal opinionated (it's built into our architecture from day 1, but you choose providers)
- Flow / agent neutral (it's a layer above us)
- Quality control opinionated (we encourage regression tests for plugins)
- Cloud neutral (offer containers, offer serverless, ...)

**Why not use OpenAPI/Swagger?**

OpenAPI (previously, Swagger) was released over a decade ago as a replacement to WSDL, where they switched the interface description from XML to JSON. Both WSDL and OpenAPI focused on the machine-to-machine use case. They answered the question, how can we describe an API in a formal manner to bind a client with a service. OpenAPI describes many of the concepts needed, but falls short in the new GPT oriented requirements.

### About OpenPlugin Manifest:

The OpenPlugin Manifest is a superset of the OpenAPI effort. It focuses on improving a few key areas including:
- Accuracy is a core element
- Emphasis on quality: linked to regression tests
- Integration w/marketplace a priority
- Ensure security; agent oriented reputation

  
### Basic Scenario
 
 Target Plugin: Google Finance API
 
 Input Request: "get the stock price for Amazon."
 
 Optional Responses:
 1. standard JSON response object
 2. a formatted response (HTML, Markdown, JSX, ...)
 3. a multimodal response (text-to-voice, image, ...)

### Usage: starting an openplugin server

##### Starting Openplugin server from PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-server
```

##### Starting Openplugin server from docker

```
#TODO
```

##### Starting Openplugin server from code

```
git clone <openplugin>
cd openplugin
poetry install
python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

### Usage: build an openplugin

##### Build an openplugin manifest in your text editor

```
#TODO
```


### Usage: run an openplugin

##### Run an openplugin using PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-servero
openplugin run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

##### Run an openplugin using server API

```
#TODO
```

##### Run an openplugin using code

```
#TODO
```

##### Run an openplugin using openplugin-sdk

```
#TODO
```





