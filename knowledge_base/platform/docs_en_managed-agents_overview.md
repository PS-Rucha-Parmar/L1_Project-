---
title: "Claude Managed Agents overview - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/managed-agents/overview"
library: "platform"
created: "2026-07-13T07:35:36.094121+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Anthropic offers two ways to build with Claude, each suited to different use cases:

| Messages API | Claude Managed Agents | |
|---|---|---|
| What it is | Direct model prompting access | Pre-built, configurable agent harness that runs in managed infrastructure | 
| Best for | Custom agent loops and fine-grained control | Long-running tasks and asynchronous work | 
| Learn more | Messages API docs | Claude Managed Agents docs | 

Claude Managed Agents provides the harness and infrastructure for running Claude as an autonomous agent. Instead of building your own agent loop, tool execution, and runtime, you get a fully managed environment where Claude can read files, run commands, browse the web, and execute code securely. The harness supports built-in prompt caching, compaction, and other performance optimizations for high-quality, efficient agent outputs.

Claude Managed Agents is also available on Claude Platform on AWS, with some differences in feature availability and session behavior. See Claude Managed Agents in the Claude Platform on AWS guide.

Create your first agent session

Create a session and send your first event

Event types, rate limits, CLI flags, and other lookup tables

Claude Managed Agents is built around four concepts:

| Concept | Description | 
|---|---|
| Agent | The model, system prompt, tools, MCP servers, and skills | 
| Environment | Configuration for where sessions run: an Anthropic-managed cloud sandbox, or a self-hosted sandbox on your own infrastructure | 
| Session | A running agent instance within an environment, performing a specific task and generating outputs | 
| Events | Messages exchanged between your application and the agent (user turns, tool results, status updates) | 

Create an agent

Define the model, system prompt, tools, MCP servers, and skills. Create the agent once and reference it by ID across sessions.

Create an environment

Configure where the agent runs: a cloud sandbox, or a self-hosted sandbox on your own infrastructure.

Start a session

Launch a session that references your agent and environment configuration.

Send events and stream responses

Send user messages as events. Claude autonomously executes tools and streams back results through server-sent events (SSE). Event history is persisted server-side and can be fetched in full.

Steer or interrupt

Send additional user events to guide the agent mid-execution, or interrupt it to change direction.

Claude Managed Agents is best for workloads that need:

Claude Managed Agents gives Claude access to a set of built-in tools:

See Tools for the full list and configuration options.

Claude Managed Agents is currently in beta. All Managed Agents endpoints require the `managed-agents-2026-04-01` beta header. The SDK sets the beta header automatically. Behaviors may be refined between releases to improve outputs.

To get started, you need:

`managed-agents-2026-04-01` beta header on all requestsWithin the beta, MCP tunnels and dreaming are in a more limited research preview. Request access to enable them.

Claude Managed Agents is stateful by design: sessions are long-running, resume cleanly after pauses, and store conversation history, sandbox state, and outputs server-side. Because of this, Managed Agents is not currently eligible for Zero Data Retention or HIPAA Business Associate Agreement (BAA) coverage. You retain control over this data: you can delete sessions, and separately delete any files you uploaded, at any time through the API. For eligibility across all features, see API and data retention.

See Rate limits and Branding guidelines in the reference.

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

- Source: [https://platform.claude.com/docs/en/managed-agents/overview](https://platform.claude.com/docs/en/managed-agents/overview)
