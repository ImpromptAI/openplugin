![Alt text](docs/openplugin_logo.jpg?raw=75x75 "Logo")
### Who is this project for?

This project is for plugin platform providers (i.e., those who want to create a container / execution environment that run the plugins). This is a Service Provider interface. In other words, we’re clearly separating ‘those who create plugins’ from ‘platforms that run plugins’. If your an application developer wanting to create a plugin, this project is likely not for you. But, you should be ensuring that the plugin framework you choose has an OpenPlugin interface. 

### Terminology
Unfortunately, as this is an emerging space, there are lots of competing terms floating around. Specific to this project, here are the definitions we’re using:

<ol>
<b><li>Plugin</li></b>
First, it’s assumed that we mean “an LLM plugin”. A plugin is the technology an end user would add to a chat app or similar to leverage 3rd party tools like APIs. 
<b><li>Plugin Manifest</li></b>
This is the metadata associated with a plugin that users or programs can view to determine how to install it, and call it.
<b><li>Tool Selector</li></b>
This refers to solutions that execute the natural language and map it to an API. Typically this is done by a platform vendor (Microsoft, Google, HuggingFace) or a library (LangChain, Imprompt). 
<b><li>Tool Selector API/ Bindings</li></b>
The process of mapping natural language to a tool can be modularized, and made a dedicated task. This task can be called via a RESTful API call, or locally via a language specific binding (SDK).
</ol>

# Tool Selectors & Use with LLMs 

Large Language Models (LLMs) are able to provide analysis on a wide range of tasks. However, there are certain limitations. In some cases, the LLMs do poorly on multi-step tasks such as solving complex mathematical problems or analyzing a complex business problem. It is also common for the LLM to need access to data that resides inside of a database, or application. In such cases, the LLM would be fed data called by an API or a query (SQL, etc.). 

Hence, there is a need to create a bridge between a user’s text, the LLM, and a structured interface like an API. These bridges go by different names. OpenAI calls them Plugins, LangChain calls them Agents, and the academic research will often call them tool selectors. Regardless of the name, the concept remains the same, and for LLMs to succeed in most complex tasks, it is essential to have a highly performant solution. 

![Alt text](docs/flow_img.png?raw=true "Flow")

## The Problem Statement
Here’s a quick overview of the problem from a developer’s viewpoint:

When people give instructions to an LLM (via chat, etc.), they use a variety of ways of describing what they want. Some technology (the tool selector) must determine what the intent of the command was (aka, intent detection). Additionally, the command might have some extra data like “in the morning”, “once per week”. All of this natural language needs to be mapped back to an API. The Tool Selector must do more than just ‘find the right tool’, it must map language to an API and call it perfectly. 

So, here we go. Given J variations of sample input text, and K variations of "installed" plugins, use a Tool Selector. Then, evaluate the performance:
<ol>
<li>Is the correct plugin selected?</li>
<li>Is the correct API operation selected?</li>
<li>Are the API parameters filled in correctly?</li>
<li>What was the cost to solve?</li>
<li>And, what was the round-trip latency?</li>
If the developer is using a composable tool selector like LangChain,  we add the following considerations: 
<li>How do the accuracy, cost and latency metrics change, when you swap out LLM providers & models (Palm2, GPT4, Cohere Command, etc.)</li>
</ol>

## Approaches to Solving the Problem 
Using NLP terms, we’d describe the problem as ‘intent detection’ + ‘slot filling’. And normally, this would be accomplished by building/fine-tuning a model specifically for your task. But with LLMs, developers are also just asking the LLM to solve the problem. There are pros and cons to the various approaches. 


T = Tool / plugin Selection <br>
O = Operation Selection <br>
P = Parameter Filling 


<b>Style 1:</b> T=LLM, O=LLM, P=LLM, <Invoke API>, Results fed back to LLM
<ul>
<li>The LLM is fed a list of ‘installed plugins’ and the user’s text.</li>
<li>The LLM is asked to decide which plugin/operation to use </li>
<li>The LLM slot fills the parameters and generates the calling code</li>
<li>The code is run; the results are either returned as-is, or are sent back to the LLM to be ‘prettified’</li>
</ul>
<b>Style 2:</b> T=Embeddings, O=LLM, P=LLM, <Invoke API>, Results fed back to LLM
<ul>
<li>Same as Style 1, but Embeddings or another ‘fast semantic matching technique is used for the ‘selector’ function.<\li>
</ul>
<b>Style 3:</b> T, O, P = Fine Tuned LLM, <Invoke API>, Results fed back to LLM
<ul>
<li>The LLM is fine tuned with training data that shows mappings between sample commands and the matching / resulting API calls.</li>
</ul>
<b>Style 4:</b> T, O, P = Single Task Model, <Invoke API>, Results fed back to LLM
<ul>
<li>A specialized, single task model is built to solve the problem. Similar to Style 3, the model is trained with your data, but on a more focused / specialized level, reducing the number of runtime inferences.</li>
</ul>
<b>Style 5:</b> Something else?
<ul>
<li>There are lots of ways to solve this problem. It’s still early-days and the best/right approach is likely still ahead of us!!</li>
</ul>


### Standardizing the Interface for Tool Selection
Developers want to create plugins that are consistently accurate and have low latency. And they want to avoid manually rewriting, redeploying and retesting their plugins across providers. If there was only one plugin hoster, it would be a trivial problem. But, as the number of chat sites/apps increases, quality assurance becomes a significant issue. 

For this reason, we’re introducing a standard interface to test plugins / tools:

 - LLM Tool Selector API (Docs) (OpenAPI JSON)

And bindings / SDK’s:
 - LangChain Binding

### Hosted Tool Selector API Providers
For demo purposes only, we’re hosting an instance of the Tool Selector API. To use the service, you’ll need to get a key from jeffrschneider[at]gmail[dot]com   

The service will limit the number of calls you can make. If you’re interested in either having a 3rd party run this as a managed service or being a managed service provider, let us know. 

### Getting started

#### Installation
To install using pip, run:
```sh
pip install openplugin
```
You can verify you have openplugin installed by running:
```sh
openplugin --help
```

#### Credentials
Before you run the application, be sure you have credentials configured.
```sh
export OPENAI_API_KEY=<your key> // if you want to use OpenAI LLM
export COHERE_API_KEY=<your key> // if you wan to use Cohere LLM
export GOOGLE_APPLICATION_CREDENTIALS=<credential_file_path: /usr/app/application_default_credentials.json> // if you want to use Google LLM
export PORT=<port: 8012> // if you want to use a different port
```

#### Usage
To start the openplugin implementation server, run:
```sh
openplugin start-server
```

OpenAPI Specification(In progress): https://raw.githubusercontent.com/LegendaryAI/openplugin/main/docs/openapi.json

#### Docker

Passing environment variables in the startup script:

```sh
docker run --name [container-name] -p 8012:8012 -e "OPENAI_API_KEY=<your_key>" -e "COHERE_API_KEY=<your_key>" -e "GOOGLE_APPLICATION_CREDENTIALS=<your_key>" -d shrikant14/openplugin:latest
```

Passing environment variables as a file

```sh
  nano [env-filename]
  Add to file
	  [variable1-name]=[value1]
	  [variable2-name]=[value2]
	  [variable3-name]=[value3]
  docker run --name [container-name] -p 8012:8012 --env-file my_env.env -d shrikant14/openplugin:latest
```

If you want to pass environment variable as a file, you can use the following command:
```sh
nano [env-filename]
#Add your environment variables in the file
OPENAI_API_KEY=[value1]
COHERE_API_KEY=[value2]
GOOGLE_APPLICATION_CREDENTIALS=[value3]
  
docker run --name [container-name] -p 8012:8012 --env-file [path-to-env-file] -d shrikant14/openplugin:latest
```
#### API USAGE

Hosted API Spec: https://api.imprompt.ai/openplugin/api/openapi.json

Example
```sh
API Endpoint: https://api.imprompt.ai/openplugin/api/run-plugin
Method: POST
HEADERS: {
  'x-api-key': 'your-api-key'
  'Content-Type': 'application/json'
}
Body: {
	"messages": [{
        "content":"Show me 5 t shirts?",
        "message_type":"HumanMessage"
    }],
	"tool_selector_config": {
        "provider":"OpenAI",
        "pipeline_name":"default"
    },
	"plugins": [{
        "manifest_url":"https://www.klarna.com/.well-known/ai-plugin.json"
    }],
	"config": {},
	"llm": {
        "provider":"OpenAIChat",
        "model_name":"gpt-3.5-turbo-0613"
    }
}
```

#### API Body Parameters

Represents the request body for running the plugin.

| Field                 | Type               | Description                                       |
| --------------------- |--------------------| ------------------------------------------------- |
| messages              | Array of Message   | The list of messages to be processed.             |
| tool_selector_config  | ToolSelectorConfig | The configuration for the tool selector.          |
| plugins               | Array of Plugin    | The list of plugins to be executed.               |
| config                | Config             | The API configuration for the plugin.             |
| llm                   | LLM                | The configuration for the LLM (Language Model) provider. |


**Message**

Represents a prompt to be executed.

| Field        | Type         | Description                                    |
| ------------ | ------------ | ---------------------------------------------- |
| content      | string       | The content of the message.                     |
| message_type | MessageType  | The type of the message.                        |


**MessageType** 

[HumanMessage, AIMessage, SystemMessage, FunctionMessage]

**ToolSelectorConfig**

Represents the configuration for a Tool Selector.


| Field           | Type                 | Description                                       |
| --------------- | -------------------- | ------------------------------------------------- |
| provider        | ToolSelectorProvider | The provider for the Tool Selector.               |
| pipeline_name   | string               | The name of the pipeline for the Tool Selector.   |


An enumeration for different Tool Selector providers= [ Langchain, Imprompt, OpenAI]

**Plugin**

Represents a plugin configuration.

| Field                     | Type      | Description                                      |
| ------------------------- | --------- | ------------------------------------------------ |
| schema_version            | string    | The version of the plugin schema.                |
| name_for_model            | string    | The name of the plugin for the model.            |
| name_for_human            | string    | The name of the plugin for human reference.      |
| description_for_model     | string    | The description of the plugin for the model.     |
| description_for_human     | string    | The description of the plugin for human reference. |
| logo_url                  | string    | The URL of the plugin's logo.                    |
| contact_email             | string    | The contact email for the plugin.                |
| legal_info_url            | string    | The URL for legal information about the plugin.  |
| manifest_url              | string    | The URL of the plugin manifest.                  |
| api                       | PluginAPI | The API configuration for the plugin.            |


**PluginAPI**

Represents the API configuration for a plugin.

| Field              | Type            | Description                                              |
| ------------------ | --------------- | -------------------------------------------------------- |
| type               | string          | The type of the API.                                     |
| url                | string          | The URL of the API.                                      |
| has_user_authentication | boolean     | Indicates if the API requires user authentication.        |
| api_endpoints      | array of string | The list of API endpoints provided by the plugin.         |


**Config**

Represents the API configuration for a plugin.

| Field            | Type   | Description                |
| ---------------- | ------ | -------------------------- |
| openai_api_key   | string | The OpenAI API key.        |


**LLM**

Represents the configuration for an LLM (Language Model) provider.

| Field              | Type          | Description                                        |
| ------------------ | ------------- | -------------------------------------------------- |
| provider           | LLMProvider   | The provider for the LLM.                          |
| model_name         | string        | The name of the LLM model.                         |
| temperature        | number        | The temperature parameter for generating output.   |
| max_tokens         | integer       | The maximum number of tokens in the generated output. |
| top_p              | number        | The top-p parameter for generating output.         |
| frequency_penalty  | number        | The frequency penalty for generating output.       |
| presence_penalty   | number        | The presence penalty for generating output.        |
| n                  | number        | The n parameter for generating output.             |
| best_of            | number        | The best-of parameter for generating output.       |
| max_retries        | integer       | The maximum number of retries for generating output. |


**LLMProvider**

An enumeration for different LLM providers. [OpenAI, OpenAIChat, GooglePalm, Cohere]