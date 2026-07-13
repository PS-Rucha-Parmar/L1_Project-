---
title: "Documentation - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/home"
library: "platform"
created: "2026-07-13T07:34:33.894310+00:00"
---

# Overview

Claude Platform

# Start building with Claude

Everything you need to integrate Claude into your applications. From first API call to production.

What do you want to build?

⌘K

```
import anthropic
client = anthropic.Anthropic()
message = client.messages.create(
  model="claude-opus-4-8",
  max_tokens=1024,
  messages=[{
    "role": "user",
    "content": "Hello, Claude"
  }]
)
print(message.content[0].text)
```
Platform

## Choose how you build

Pick the developer surface that matches your approach, and the infrastructure that fits your stack.

### Messages

Direct model access. You construct every turn, manage conversation state, and write your own tool loop.

### Managed Agents

Fully managed agent infrastructure. Deploy and manage autonomous agents in stateful sessions with persistent event history.

Developer journey

## From idea to production

Follow the lifecycle or jump to what you need.

- ### Get started
- ### Build
- ### Evaluate and ship
- ### Operate

Models

## The Claude model family

Choose the right model for your use case.

Resources

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

- Source: [https://platform.claude.com/docs/en/home](https://platform.claude.com/docs/en/home)
