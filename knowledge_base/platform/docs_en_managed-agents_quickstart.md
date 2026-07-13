---
title: "Get started with Claude Managed Agents - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/managed-agents/quickstart"
library: "platform"
created: "2026-07-13T07:40:20.274362+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This guide walks you through creating an agent, setting up an environment, starting a session, and streaming agent responses.

**Prefer an interactive walkthrough?** Run `/claude-api managed-agents-onboard` in the latest version of Claude Code for a guided setup and interactive question-answering.

| Concept | Description | 
|---|---|
| Agent | The model, system prompt, tools, MCP servers, and skills | 
| Environment | Configuration for where sessions run: an Anthropic-managed cloud sandbox, or a self-hosted sandbox on your own infrastructure | 
| Session | A running agent instance within an environment, performing a specific task and generating outputs | 
| Events | Messages exchanged between your application and the agent (user turns, tool results, status updates) | 

Check the installation:

`ant --version`Set your API key as an environment variable:

`export ANTHROPIC_API_KEY="your-api-key-here"`Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See Beta headers.

Create an agent

Create an agent that defines the model, system prompt, and available tools.

```
ant beta:agents create \
  --name "Coding Assistant" \
  --model '{id: claude-opus-4-8}' \
  --system "You are a helpful coding assistant. Write clean, well-documented code." \
  --tool '{type: agent_toolset_20260401}'
```
The `agent_toolset_20260401` tool type enables the full set of pre-built agent tools (bash, file operations, web search, and more). See Tools for the complete list and per-tool configuration options.

Save the returned `agent.id`. You'll reference it in every session you create.

Create an environment

An environment defines the sandbox where your agent runs.

```
ant beta:environments create \
  --name "quickstart-env" \
  --config '{type: cloud, networking: {type: unrestricted}}'
```
Save the returned `environment.id`. You'll reference it in every session you create.

Start a session

Create a session that references your agent and environment.

```
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    title="Quickstart session",
)
print(f"Session ID: {session.id}")
```
Send a message and stream the response

Open a stream, send a user event, then process events as they arrive:

```
with client.beta.sessions.events.stream(session.id) as stream:
    # Send the user message after the stream opens
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
                    },
                ],
            },
        ],
    )
    # Process streaming events
    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```
The agent writes a Python script, executes it in the sandbox, and verifies the output file was created. Your output looks similar to this:

```
I'll create a Python script that generates the first 20 Fibonacci numbers and saves them to a file.
[Using tool: write]
[Using tool: bash]
The script ran successfully. Let me verify the output file.
[Using tool: bash]
fibonacci.txt contains the first 20 Fibonacci numbers (0 through 4181).
Agent finished.
```
When you send a user event, Claude Managed Agents:

`session.status_idle` event when it has nothing more to do.Create reusable, versioned agent configurations

Customize networking and sandbox settings

Enable specific tools for your agent

Handle events and steer the agent mid-execution

Run your agent on a recurring cron schedule

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

- Source: [https://platform.claude.com/docs/en/managed-agents/quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart)
