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

### Starting a Server

#### 1. Starting an OpenPlugin Server from PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-server
```

#### 2. Starting OpenPlugin Server from Docker

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

#### 3. Starting an OpenPlugin Server from code

```
git clone <openplugin>
cd openplugin
poetry install
python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

### Run an OpenPlugin

#### 1. Run an OpenPlugin using PyPI

```
pip install openplugin
openplugin --help
export OPENAI_API_KEY=<your key>
openplugin start-servero
openplugin run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"
```

#### 2. Run via an API call 

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

#### 3. Run via Code

```
pip install openplugin

from openplugin.core.plugin_runner import run_prompt_on_plugin
openplugin=""
prompt=""
response =await run_prompt_on_plugin(openplugin, prompt)
```

#### 4. Run via SDK

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





