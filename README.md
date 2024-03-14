<h1 align="center">
        OpenPlugin
    </h1>
    <p align="center">
        <p align="center">:open_hands::electric_plug: Multimodal API Bridge - make APIs into chat and multimodal ready interfaces
        <br>
    </p>
<h4 align="center">
    <a href="https://openplugin.com/" target="_blank">
        <img src="https://img.shields.io/badge/view-documentation-blue" alt="View Documentation">
    </a>
    <a href="https://pypi.org/project/openplugin/" target="_blank">
        <img src="https://img.shields.io/pypi/v/openplugin.svg" alt="PyPI Version">
    </a>
</h4>

![Openplugin banner image](docs/source/_images/openplugin_hero_header.png)


This is an open source effort to create an ecosystem around LLM enabled APIs. We make it easy to "chat with an API", that is, to send natural language as the input to the API and have it process it. Then, we offer several options to easily transform the APIs response into something better suited for human consumption like text, markdown, HTML, JSX, voice, video, etc.

---

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

**NOTE**: Please see the complete documentation here: https://openplugin.com/

## About OpenPlugin Manifest:

The OpenPlugin Manifest is a superset of the OpenAPI effort. It focuses on improving a few key areas including:
- Accuracy is a core element
- Emphasis on quality: linked to regression tests
- Integration w/marketplace a priority
- Ensure security; agent oriented reputation

**Why not use OpenAPI/Swagger?**

OpenAPI (previously, Swagger) was released over a decade ago as a replacement to WSDL, where they switched the interface description from XML to JSON. Both WSDL and OpenAPI focused on the machine-to-machine use case. They answered the question, how can we describe an API in a formal manner to bind a client with a service. OpenAPI describes many of the concepts needed, but falls short in the new GPT oriented requirements.

## Architecture

<div align="center">
    <img src="docs/source/_images/architecture.png" alt="Openplugin banner image" height="300">
</div>

### Basic Scenario
 
 Target Plugin: Google Finance API
 
 Input Request: "get the stock price for Amazon."
 
 Optional Responses:
 1. standard JSON response object
 2. a formatted response (HTML, Markdown, JSX, ...)
 3. a multimodal response (text-to-voice, image, ...)


### Usage: starting an openplugin server

#### 1. Starting Openplugin server from PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-server
```

#### 2. Starting Openplugin server from docker

```
# Passing environment variables in the startup script
docker run --name openplugin_container -p 8006:8006 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest
  

# Passing environment variables as a file
nano [env-filename]
Add to file
    [variable1-name]=[value1]
    [variable2-name]=[value2]
    [variable3-name]=[value3]
docker run --name openplugin_container -p 8006:8006 --env-file my_env.env -d shrikant14/openplugin:latest

```

#### 3. Starting OpenPlugin server from code

```
git clone <openplugin>
cd openplugin
poetry install
python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

### Usage: build an OpenPlugin

##### Build an OpenPlugin manifest in your text editor

```
COMING SOON
```


### Usage: run an OpenPlugin

#### 1. Run an OpenPlugin using PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-servero
openplugin run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

#### 2. Run an OpenPlugin using server API

```
curl --location 'https://api.imprompt.ai/openplugin/api/plugin-execution-pipeline' \
           --header 'Content-Type: application/json' \
           --header 'x-api-key: 'YOUR-API-KEY' \
           --data '{
            "prompt": "USER_PROMPT",
            "conversation": [],
            "openplugin_manifest_url": "MANIFEST_URL",
            "header":{},
            "approach": {
              "base_strategy": "oai functions",
              "llm": {
                "frequency_penalty": 0,
                "max_tokens": 2048,
                "model_name": "gpt-3.5-turbo-0613",
                "presence_penalty": 0,
                "provider": "OpenAI",
                "temperature": 0,
                "top_p": 1
              },
              "name": "OAI functions-OpenAI",
              "pre_prompt": null
            },
            "output_module_names":["default_cleanup_response"]
            }'
```

#### 3. Run an OpenPlugin using code

```
pip install openplugin

from openplugin.core.plugin_runner import run_prompt_on_plugin
openplugin=""
prompt=""
response =await run_prompt_on_plugin(openplugin, prompt)
```

#### 4. Run an OpenPlugin using openplugin-sdk

**NOTE:** Learn more about openplugin-sdk at: https://github.com/ImpromptAI/openplugin-sdk

```
pip install openplugin-sdk

remote_server_endpoint = "...."
openplugin_api_key = "...."
svc = OpenpluginService(
        remote_server_endpoint=remote_server_endpoint, api_key=openplugin_api_key
)

openplugin_manifest_url = "...."
prompt = "..."
output_module_name="..."

response = svc.run(
        openplugin_manifest_url=openplugin_manifest_url,
        prompt=prompt,
        output_module_names=[output_module_name],
)
print(f"Response={response.value}")
```





