---
title: "Claude in Microsoft Foundry - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry"
library: "platform"
created: "2026-07-13T07:42:57.202242+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This guide shows you how to set up and make API calls to Claude in Microsoft Foundry using one of Anthropic's client SDKs or direct HTTP requests. When you access Claude in Microsoft Foundry, you are billed for Claude usage in the Azure Marketplace. You can use the latest Claude models, including Claude Opus 4.8 and Claude Sonnet 5, and features such as the 1M-token context window, while managing costs through your Azure subscription.

Claude is available in Global Standard and US Data Zone Standard deployment types in Foundry resources, billed in Claude Consumption Units through the Azure Marketplace. Visit Claude in Microsoft Foundry pricing for details.

Claude models in Microsoft Foundry are available in two hosting options. You choose the hosting option when you configure the deployment.

| Hosted on Azure | Hosted on Anthropic | |
|---|---|---|
| Where inference runs | Anthropic-operated service running on Azure infrastructure | Anthropic-operated service running on Anthropic infrastructure | 
| Model availability | The latest models in the Opus, Sonnet, and Haiku families | All Claude models available on Microsoft Foundry | 
| Deployment types | Global Standard, US Data Zone Standard | Global Standard | 
| Recommended for | Most workloads | Access to features or models not yet hosted on Azure | 

Anthropic acts as an independent processor for Microsoft. Customers using Claude through Microsoft Foundry are subject to Anthropic's data use terms. For deployments hosted on Azure, prompts and completions remain within Azure. Only usage metadata and content flagged by Anthropic's safety systems egress to Anthropic. Anthropic continues to provide its safety and data commitments.

Before you begin, ensure you have:

Anthropic's client SDKs support Foundry through a platform-specific package or client class. The examples on this page also show requests with cURL and the ant CLI. To set up the CLI, see CLI quickstart.

Foundry is supported by the C#, Java, PHP, Python, and TypeScript SDKs. Foundry is not currently available in the Go and Ruby SDKs.

Foundry uses a two-level hierarchy: **resources** contain your security and billing configuration, while **deployments** are the model instances you call through the API. You'll first create a Foundry resource, then create one or more Claude deployments within it.

Create a Foundry resource, which is required to use and manage services in Azure. You can follow these instructions to create a Foundry resource. Alternatively, you can start by creating a Foundry project, which involves creating a Foundry resource.

To provision your resource:

`{resource}` in API endpoints (for example, `https://{resource}.services.ai.azure.com/anthropic/v1/*`).After creating your resource, deploy a Claude model to make it available for API calls. These steps describe the new Foundry portal (the **New Foundry** toggle is on):

`my-claude-deployment`). The deployment name cannot be changed after creation.`inference_geo: "us"` on the Claude API.If the **New Foundry** toggle is off, you are in the classic portal layout. There, open **Model catalog** in the left pane to find and deploy a model, and open **Models + endpoints** (under **My assets**) to view your deployments and their endpoint details.

The deployment name you choose becomes the value you pass in the `model` parameter of your API requests. You can create multiple deployments of the same model with different names to manage separate configurations or rate limits.

Claude in Microsoft Foundry supports two authentication methods: API keys and Entra ID tokens. Both methods use Azure-hosted endpoints in the format `https://{resource}.services.ai.azure.com/anthropic/v1/*`.

After provisioning your Foundry Claude resource, you can obtain an API key from the Foundry portal:

`api-key` or `x-api-key` header in your requests, or provide it to the SDK.The Foundry SDKs require an API key and either a resource name or base URL. The C#, Java, PHP, Python, and TypeScript SDKs automatically read these from the following environment variables if they are defined:

`ANTHROPIC_FOUNDRY_API_KEY` - Your API key`ANTHROPIC_FOUNDRY_RESOURCE` - Your resource name (for example, `example-resource`)`ANTHROPIC_FOUNDRY_BASE_URL` - Alternative to resource name: the full base URL (for example, `https://example-resource.services.ai.azure.com/anthropic/`). The C# SDK does not read this variable: it always constructs the base URL from the resource name.The `resource` and `base_url` parameters are mutually exclusive. Provide either the resource name (which the SDK uses to construct the URL as `https://{resource}.services.ai.azure.com/anthropic/`) or the full base URL directly.

**Example using API key:**

```
import os
from anthropic import AnthropicFoundry
client = AnthropicFoundry(
    api_key=os.environ.get("ANTHROPIC_FOUNDRY_API_KEY"),
    resource="example-resource",  # your resource name
)
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message.content)
```
Keep your API keys secure. Never commit them to version control or share them publicly. Anyone with access to your API key can make requests to Claude through your Foundry resource.

Entra ID authentication lets you manage access with Azure RBAC, integrate with your organization's identity management, and avoid handling API keys manually. To use Entra ID tokens:

`Authorization: Bearer {TOKEN}` header.**Example using Entra ID:**

```
from anthropic import AnthropicFoundry
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# Get Microsoft Entra ID token using token provider pattern
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
# Create client with Entra ID authentication
client = AnthropicFoundry(
    resource="example-resource",  # your resource name
    azure_ad_token_provider=token_provider,  # Use token provider for Entra ID auth
)
# Make request
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message.content)
```
Foundry includes request identifiers in HTTP response headers for debugging and tracing. When contacting support, provide both the `request-id` and `apim-request-id` (Azure API Management) values to help teams quickly locate and investigate your request across both Anthropic and Azure systems.

Claude in Microsoft Foundry supports most Claude features. You can find all the features currently supported in Features overview.

Claude Fable 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a 1M-token context window on Microsoft Foundry. Other Claude models, including Claude Sonnet 4.5, have a 200k-token context window.

`fallbacks` parameter; use the client-side fallback pattern instead)The following features are available for deployments hosted on Anthropic but are not supported for deployments hosted on Azure:

Requests that use these features against a deployment hosted on Azure return a `400 Bad Request` error by design. Claude Code detects deployments hosted on Azure and automatically adapts its feature set.

API responses from Claude in Microsoft Foundry follow the standard Claude API response format. This includes the `usage` object in response bodies, which provides detailed token consumption information for your requests. The `usage` object is consistent across all platforms (Claude API, Foundry, Claude Platform on AWS, Amazon Bedrock, and Google Cloud).

For details on response headers specific to Foundry, see Correlation request IDs.

Lifecycle terms (Deprecated, Retired) are defined in Model deprecations. Microsoft Foundry follows the Claude API lifecycle schedule.

The following Claude models are available through Foundry:

| Model | Default deployment name | Hosted on Azure | Hosted on Anthropic | 
|---|---|---|---|
| Claude Fable 5 | claude-fable-5 | ✓ | |
| Claude Opus 4.8 | claude-opus-4-8 | ✓ | ✓ | 
| Claude Opus 4.7 | claude-opus-4-7 | ✓ | |
| Claude Opus 4.6 | claude-opus-4-6 | ✓ | |
| Claude Opus 4.5 | claude-opus-4-5 | ✓ | |
| Claude Opus 4.1 Deprecated. Retiring August 5, 2026. | claude-opus-4-1 | ✓ | |
| Claude Sonnet 5 | claude-sonnet-5 | ✓ | ✓ | 
| Claude Sonnet 4.6 | claude-sonnet-4-6 | ✓ | |
| Claude Sonnet 4.5 | claude-sonnet-4-5 | ✓ | |
| Claude Haiku 4.5 | claude-haiku-4-5 | ✓ | ✓ | 

By default, deployment names match the model IDs shown in the preceding table. However, you can create custom deployments with different names in the Foundry portal to manage different configurations, versions, or rate limits. Use the deployment name (not necessarily the model ID) in your API requests.

Claude Mythos Preview is a research preview available to invited customers on Microsoft Foundry.

Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See Migrating to a newer Claude model.

Claude in Microsoft Foundry bills through the Azure Marketplace. Usage is denominated in Claude Consumption Units (CCUs), metered hourly, and invoiced monthly in arrears on your Azure bill. CCUs are not prepaid credits. There is no CCU balance or commitment.

For the CCU price, conversion mechanics, and per-model token rates, see Claude in Microsoft Foundry pricing.

To move an existing deployment from one hosting option to the other:

`model` parameter.If the new deployment is in the same Foundry resource, your endpoint URL and authentication are unchanged. If you created a new resource, update your application's endpoint and credentials to point to it.

Azure provides monitoring and logging for your Claude usage through standard Azure patterns:

Anthropic recommends logging your activity on at least a 30-day rolling basis to understand usage patterns and investigate any potential issues.

Azure's logging services are configured within your Azure subscription. Enabling logging does not provide Microsoft or Anthropic access to your content beyond what's necessary for billing and service operation.

**Error:** `401 Unauthorized` or `Invalid API key`

**Error:** `403 Forbidden`

**Error:** `429 Too Many Requests`

Foundry does not include Anthropic's standard rate limit headers (`anthropic-ratelimit-tokens-limit`, `anthropic-ratelimit-tokens-remaining`, `anthropic-ratelimit-tokens-reset`, `anthropic-ratelimit-input-tokens-limit`, `anthropic-ratelimit-input-tokens-remaining`, `anthropic-ratelimit-input-tokens-reset`, `anthropic-ratelimit-output-tokens-limit`, `anthropic-ratelimit-output-tokens-remaining`, and `anthropic-ratelimit-output-tokens-reset`) in responses. Manage rate limiting through Azure's monitoring tools instead.

**Error:** `Model not found` or `Deployment not found`

**Error:** `Invalid model parameter`

Explore Claude's advanced features and capabilities.

Learn about Anthropic's pricing structure for models and features.

As safer and more capable models launch, Anthropic regularly retires older ones. See all API deprecations, along with recommended replacements.

Browse Anthropic models in the Foundry catalog.

View Microsoft's pricing details for Azure AI Foundry.

View Anthropic's per-model pricing details.

Manage your Azure resources.

Was this page helpful?

# Concepts

# Architecture

# Workflow

# API

# Parameters

# Return Values

# Code Example

# Output

# Notes

# Best Practices

# Common Mistakes

# Performance Notes

# Related Topics

# References

- Source: [https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)
