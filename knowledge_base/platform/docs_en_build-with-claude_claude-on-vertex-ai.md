---
title: "Claude on Google Cloud - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai"
library: "platform"
created: "2026-07-13T07:42:26.388911+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

The API for accessing Claude on Google Cloud's Agent Platform is nearly identical to the Messages API, with two key differences in request format:

`model` is not passed in the request body. Instead, it is specified in the Google Cloud endpoint URL.`anthropic_version` is passed in the request body (rather than as a header), and must be set to the value `vertex-2023-10-16`.Agent Platform is also supported by Anthropic's official client SDKs. This guide walks you through making a request to Claude on Agent Platform using one of Anthropic's client SDKs.

Note that this guide assumes you already have a Google Cloud project that is able to use Agent Platform. See Anthropic Claude models on Agent Platform for more information on the setup required and a full walkthrough.

First, install Anthropic's client SDK for your language of choice.

Note that Anthropic model availability varies by region. Search for "Claude" in the Model Garden or go to Anthropic Claude models for the latest information.

Lifecycle terms (Deprecated, Retired) are defined in Model deprecations. Lifecycle dates on partner-operated platforms are set by the partner and can differ from the Claude API schedule. For the current retirement date of any model on Agent Platform, see Google Cloud's documentation for Claude models on Agent Platform.

| Model | Agent Platform API model ID | 
|---|---|
| Claude Fable 5 | claude-fable-5 | 
| Claude Opus 4.8 | claude-opus-4-8 | 
| Claude Opus 4.7 | claude-opus-4-7 | 
| Claude Opus 4.6 | claude-opus-4-6 | 
| Claude Sonnet 5 | `claude-sonnet-5` | 
| Claude Sonnet 4.6 | claude-sonnet-4-6 | 
| Claude Sonnet 4.5 | claude-sonnet-4-5@20250929 | 
| Claude Sonnet 4 Deprecated. | claude-sonnet-4@20250514 | 
| Claude Sonnet 3.7 Retired. | claude-3-7-sonnet@20250219 | 
| Claude Opus 4.5 | claude-opus-4-5@20251101 | 
| Claude Opus 4.1 Deprecated. | claude-opus-4-1@20250805 | 
| Claude Opus 4 Deprecated. | claude-opus-4@20250514 | 
| Claude Haiku 4.5 | claude-haiku-4-5@20251001 | 
| Claude Haiku 3.5 Deprecated. | claude-3-5-haiku@20241022 | 

Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See Migrating to a newer Claude model.

Before running requests you may need to run `gcloud auth application-default login` to authenticate with Google Cloud.

The following examples show how to generate text from Claude on Agent Platform:

```
from anthropic import AnthropicVertex
project_id = "MY_PROJECT_ID"
region = "global"
client = AnthropicVertex(project_id=project_id, region=region)
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude!",
        }
    ],
)
print(message)
```
See the client SDKs and the official Agent Platform docs for more details.

Claude is also available through Amazon Bedrock, Claude Platform on AWS, and Microsoft Foundry.

Data handling for this offering is governed by Google Cloud. For details, see Agent Platform and zero data retention.

Agent Platform provides a request-response logging service that allows customers to log the prompts and completions associated with your usage.

Anthropic recommends that you log your activity on at least a 30-day rolling basis in order to understand your activity and investigate any potential misuse.

Turning on this service does not give Google or Anthropic any access to your content.

For the full feature list with Google Cloud availability, see Features overview.

`fallbacks` parameter; use the client-side fallback pattern instead)Claude Fable 5, Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6 have a 1M-token context window on Agent Platform. Other Claude models, including Sonnet 4.5 and Sonnet 4 (deprecated), have a 200k-token context window.

Agent Platform limits request payloads to 30 MB. When sending large documents or many images, you may reach this limit before the token limit.

Agent Platform offers three endpoint types:

Regional and multi-region endpoints include a 10% pricing premium over global endpoints.

This applies to Claude Sonnet 4.5 and future models only. Older models (Claude Sonnet 4 (deprecated), Opus 4 (deprecated), and earlier) maintain their existing pricing structures.

**Global endpoints (recommended):**

**Multi-region endpoints:**

`us` and `eu`)**Regional endpoints:**

**Using global endpoints (recommended):**

Set the `region` parameter to `"global"` when initializing the client:

```
from anthropic import AnthropicVertex
project_id = "MY_PROJECT_ID"
region = "global"
client = AnthropicVertex(project_id=project_id, region=region)
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude!",
        }
    ],
)
print(message)
```
**Using multi-region endpoints:**

Set the `region` parameter to a multi-region identifier: `"us"` for the United States or `"eu"` for the European Union. The SDK routes requests to the corresponding multi-region endpoint (`https://aiplatform.us.rep.googleapis.com` or `https://aiplatform.eu.rep.googleapis.com`), which dynamically balances traffic across regions within that geography.

```
from anthropic import AnthropicVertex
project_id = "MY_PROJECT_ID"
region = "us"  # Multi-region identifier: "us" or "eu"
client = AnthropicVertex(project_id=project_id, region=region)
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude!",
        }
    ],
)
print(message)
```
**Using regional endpoints:**

Specify a specific region like `"us-east1"` or `"europe-west1"`:

```
from anthropic import AnthropicVertex
project_id = "MY_PROJECT_ID"
region = "us-east1"  # Specify a specific region
client = AnthropicVertex(project_id=project_id, region=region)
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hey Claude!",
        }
    ],
)
print(message)
```
Claude Mythos Preview is a research preview available to invited customers on Agent Platform. For more information, see Project Glasswing.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)
