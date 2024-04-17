==================================
OpenPlugin Manifest
==================================

The OpenPlugin Manifest is a superset of the OpenAPI effort. It focuses on improving a few key areas including:

 * Accuracy is a core element
 * Emphasis on quality: linked to regression tests
 * Integration w/marketplace a priority
 * Ensure security; agent oriented reputation

**NOTE:** This project provides a standard way to define LLM plugins and present them to various LLM engines. It is vendor neutral and meant to facilitate plugin portability across vendors and projects. The project introduces the OpenPlugin manifest file format, which allows developers to specify properties and settings for their plugins such as name, version, dependencies, and supported platforms. This format enables seamless integration with plugin platform providers.

OpenPlugin addresses the problem of mapping natural language instructions to API calls. It involves using a tool selector to determine the intent of the command and mapping it to an API.
Our reference implementation also evaluates the accuracy of the tool selector:

- selecting the correct plugin,
- selecting the correct API operation,
- filling in API parameters correctly, and
- authenticating and calling the API correctly.
- monitoring the cost and round-trip latency of solving the problem