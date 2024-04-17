==================================
Design Decisions
==================================


 - LLM neutral (LLMs leapfrog each other in capability; swap easily, support many)
 - Framework neutral (langchain, semantic kernel, ...)
 - Deployment model neutral (serverless, containers, k8, ... )
 - Language neutral (our manifest is declarative JSON)
 - Client neutral (e.g., we're not hard coded to ChatGPT or Gemini, ...)
 - Multimodal opinionated (it's built into our architecture from day 1, but you choose providers)
 - Flow / agent neutral (it's a layer above us)
 - Quality control opinionated (we encourage regression tests for plugins)
 - Cloud neutral (offer containers, offer serverless, ...)
