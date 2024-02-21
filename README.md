## :open_hands: :electric_plug: Multimodal API Bridge - Openplugin make APIs into chat and multimodal ready interfaces.


##### Please see the complete documentation here: https://openplugin.org/

#### OpenPlugin
This is an open source effort to create an ecosystem around LLM enabled APIs. We make it easy to "chat with an API", that is, to send natural language as the input to the API and have it process it. Then, we offer several options to easily transform the APIs response into something better suited to human consumption like text, markdown, HTML, JSX, voice, video, etc.

#### Design Decisions:
- LLM neutral (LLMs leapfrog each other in capability; swap easily, support many)
- Framework neutral (langchain, semantic kernel, ...)
- Deployment model neutral (serverless, containers, k8, ... )
- Language neutral (our manifest is declarative JSON)
- Client neutral (e.g., we're not hard coded to ChatGPT or Gemini, ...)
- Multimodal opinionated (it's built into our architecture from day 1, but you choose providers)
- Flow / agent neutral (it's a layer above us)
- Quality control opinionated (we encourage regression tests for plugins)
- Cloud neutral (offer containers, offer serverless, ...)


#### Why not use OpenAPI/Swagger?
OpenAPI (previously, Swagger) was released over a decade ago as a replacement to WSDL, where they switched the interface description from XML to JSON. Both WSDL and OpenAPI focused on the machine-to-machine use case. They answered the question, how can we describe an API in a formal manner to bind a client with a service. OpenAPI describes many of the concepts needed, but falls short in the new GPT oriented requirements.
The OpenPlugin Manifest is a superset of the OpenAPI effort. It focuses on improving a few key areas including:
- Accuracy is a core focus
- Emphasis on quality: linked to regression tests
- Integration w/marketplace a priority
- Ensure security; agent oriented reputation
- Extensibility: monetization

#### Usage:

#### Openplugin commands:
python openplugin/main.py --help

python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt sample_prompt.txt --log-level="FLOW"

python openplugin/main.py run-plugin --openplugin manifests/sample_klarna.json --prompt "show me some t shirts" --log-level="INFO"

#### Install Openplugin using PYPI

pip install openplugin

openplugin --help

