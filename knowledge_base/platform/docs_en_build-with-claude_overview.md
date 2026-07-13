---
title: "Features overview - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/overview"
library: "platform"
created: "2026-07-13T07:55:32.184452+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Claude's API surface is organized into five areas:

If you're new, start with model capabilities and tools. Return to the other sections when you're ready to optimize cost, latency, or scale.

For administration and governance, see the Admin API, the Usage and Cost API, and the Compliance API.

Features on the Claude Platform are assigned one of the following availability classifications per platform (shown in the Availability column of each following table). Not all features pass through every stage. A feature may enter at any classification and may skip stages.

| Classification | Description | 
|---|---|
| Beta | Preview features used for gathering feedback and iterating on a less mature use case. Availability may be limited, including through sign-up requirements or waitlists, and may not be publicly announced. Features may change significantly or be discontinued based on feedback. Not guaranteed for ongoing production use. Breaking changes are possible with notice, and some platform-specific limitations may apply. Beta features on the Claude API and Claude Platform on AWS have a beta header. | 
| Generally available (GA) | Feature is stable, fully supported, and recommended for production use. Should not have a beta header or other indicator that the feature is in a preview state. Covered by standard API versioning guarantees. | 
| Deprecated | Feature is still functional but no longer recommended. A migration path and removal timeline are provided. | 
| Retired | Feature is no longer available. | 

**Platform labels:** Claude API (Anthropic first-party) · Claude Platform on AWS (Anthropic-operated on AWS) · Bedrock (AWS-operated) · Google Cloud (Google-operated) · Microsoft Foundry (Anthropic-operated on Azure)

Ways to steer Claude and Claude's direct outputs, including response format, reasoning depth, and input modalities.

You can discover which capabilities a model supports programmatically. The Models API returns `max_input_tokens`, `max_tokens`, and a `capabilities` object for every available model.

The ZDR column indicates whether a feature is available under a Zero Data Retention arrangement. For most features this depends only on what the feature mechanism retains; for features tied to specific models, model-level ZDR availability also applies. See Model-specific data retention requirements.

| Feature | Description | Zero Data Retention (ZDR) | Availability | 
|---|---|---|---|
| Context windows | Up to 1M tokens for processing large documents, extensive code bases, and long conversations. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Adaptive thinking | Let Claude dynamically decide when and how much to think. The only thinking mode on Claude Opus 4.8 and Claude Opus 4.7. Use the effort parameter to control thinking depth. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Batch processing | Process large volumes of requests asynchronously for cost savings. Send batches with a large number of queries per batch. Batch API calls cost 50% less than standard API calls. | Not ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) | 
| Citations | Ground Claude's responses in source documents. With Citations, Claude can provide detailed references to the exact sentences and passages it uses to generate responses, leading to more verifiable, trustworthy outputs. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Data residency | Control where model inference runs using geographic controls. Specify `"global"`or`"us"`routing per request through the`inference_geo`parameter. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) | 
| Effort | Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Extended thinking | Enhanced reasoning capabilities for complex tasks, providing transparency into Claude's step-by-step thought process before delivering its final answer. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Fallback credit | Avoid paying the prompt-cache cost twice when you retry a refused request on another model. The refusal carries a credit token, and echoing it on the retry bills the retry as though the conversation had been on the new model all along. Credit tokens returned in Message Batches results cannot be redeemed. | Not ZDR eligible* | Claude API (Beta) Claude Platform on AWS (Beta) Bedrock (Beta) Google Cloud (Beta) Microsoft Foundry (Beta) | 
| PDF support | Process and analyze text and visual content from PDF documents. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Search results | Enable natural citations for RAG applications by providing search results with proper source attribution. Achieve web search-quality citations for custom knowledge bases and tools. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Server-side fallback | Retry a refused request inside a single API call. Name up to three fallback models, and when the requested model declines, the API runs the next model in the chain on the same request. The `fallbacks`parameter is not available in the Message Batches API. | Not ZDR eligible* | Claude API (Beta) Claude Platform on AWS (Beta) | 
| Structured outputs | Guarantee schema conformance with two approaches: JSON outputs for structured data responses, and strict tool use for validated tool inputs. | ZDR eligible (qualified)* | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA)† | 

Built-in tools that Claude invokes through `tool_use`. Server-side tools are run by the platform; client-side tools are implemented and executed by you.

| Feature | Description | ZDR | Availability | 
|---|---|---|---|
| Advisor tool | Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation for long-horizon agentic workloads. | ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) | 
| Code execution | Run code in a sandboxed environment for advanced data analysis, calculations, and file processing. Free when used with web search or web fetch. | Not ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Microsoft Foundry (GA)† | 
| Web fetch | Retrieve full content from specified web pages and PDF documents for in-depth analysis. | ZDR eligible* | Claude API (GA) Claude Platform on AWS (GA) Microsoft Foundry (GA)† | 
| Web search | Augment Claude's comprehensive knowledge with current, real-world data from across the web. | ZDR eligible* | Claude API (GA) Claude Platform on AWS (GA) Google Cloud (GA) Microsoft Foundry (GA)† | 

| Feature | Description | ZDR | Availability | 
|---|---|---|---|
| Bash | Execute bash commands and scripts to interact with the system shell and perform command-line operations. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Computer use | Control computer interfaces by taking screenshots and issuing mouse and keyboard commands. | ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Bedrock (Beta) Google Cloud (Beta) Microsoft Foundry (Beta) | 
| Memory | Enable Claude to store and retrieve information across conversations. Build knowledge bases over time, maintain project context, and learn from past interactions. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Text editor | Create and edit text files with a built-in text editor interface for file manipulation tasks. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 

Infrastructure that supports discovering, orchestrating, and scaling tool use.

| Feature | Description | ZDR | Availability | 
|---|---|---|---|
| Agent Skills | Extend Claude's capabilities with Skills. Use pre-built Skills (PowerPoint, Excel, Word, PDF) or create custom Skills with instructions and scripts. Skills use progressive disclosure to efficiently manage context. | Not ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Microsoft Foundry (Beta)† | 
| Fine-grained tool streaming | Stream tool use parameters without buffering/JSON validation, reducing latency for receiving large parameters. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| MCP connector | Connect to remote MCP servers directly from the Messages API without a separate MCP client. | Not ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Microsoft Foundry (Beta)† | 
| Programmatic tool calling | Enable Claude to call your tools programmatically from within code execution containers, reducing latency and token consumption for multi-tool workflows. | Not ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Microsoft Foundry (GA)† | 
| Tool search | Scale to thousands of tools by dynamically discovering and loading tools on-demand using regex-based search, optimizing context usage and improving tool selection accuracy. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA)† | 

Infrastructure for controlling and optimizing Claude's context window.

| Feature | Description | ZDR | Availability | 
|---|---|---|---|
| Compaction | Server-side context summarization for long-running conversations. When context approaches the window limit, the API automatically summarizes earlier parts of the conversation. | ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Bedrock (Beta) Google Cloud (Beta) Microsoft Foundry (Beta) | 
| Context editing | Automatically manage conversation context with configurable strategies. Supports clearing tool results when approaching token limits and managing thinking blocks in extended thinking conversations. | ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Bedrock (Beta) Google Cloud (Beta) Microsoft Foundry (Beta) | 
| Automatic prompt caching | Simplify prompt caching to a single API parameter. The system automatically caches the last cacheable block in your request, moving the cache point forward as conversations grow. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Prompt caching (5m) | Provide Claude with more background knowledge and example outputs to reduce costs and latency. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Prompt caching (1hr) | Extended 1-hour cache duration for less frequently accessed but important context, complementing the standard 5-minute cache. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 
| Token counting | Token counting enables you to determine the number of tokens in a message before sending it to Claude, helping you make informed decisions about your prompts and usage. | ZDR eligible | Claude API (GA) Claude Platform on AWS (GA) Bedrock (GA) Google Cloud (GA) Microsoft Foundry (GA) | 

Manage files and assets for use with Claude.

| Feature | Description | ZDR | Availability | 
|---|---|---|---|
| Files API | Upload and manage files to use with Claude without re-uploading content with each request. Supports PDFs, images, and text files. | Not ZDR eligible | Claude API (Beta) Claude Platform on AWS (Beta) Microsoft Foundry (Beta)† | 

* **Structured outputs:** Your prompts and Claude's outputs are not stored. Only JSON schemas are cached, for up to 24 hours since last use. **Web search and web fetch:** ZDR-eligible except when dynamic filtering is enabled. **Fallback credit and server-side fallback:** The features retain no message content, but both handle refusals from Claude Fable 5, which is not available under ZDR. See ZDR details.

† On Microsoft Foundry, feature availability differs by hosting option. These features are available on Hosted on Anthropic deployments, and not on Hosted on Azure deployments.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/overview](https://platform.claude.com/docs/en/build-with-claude/overview)
