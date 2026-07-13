---
title: "Define your agent - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/managed-agents/agent-setup"
library: "platform"
created: "2026-07-13T07:41:23.674538+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

An agent is a reusable, versioned configuration that defines persona and capabilities. It bundles the model, system prompt, tools, MCP servers, and skills that shape how Claude behaves during a session.

Create the agent once as a reusable resource and reference it by ID each time you start a session. Agents are versioned and easier to manage across many sessions.

Managed Agents API requests require the `managed-agents-2026-04-01` beta header, except memory store endpoints, which use `agent-memory-2026-07-22` instead. The SDK sets the correct beta header automatically. See Beta headers.

| Field | Description | 
|---|---|
| `name` | Required. A human-readable name for the agent. | 
| `model` | Required. The Claude model that powers the agent. Accepts a model ID string or an object, for example `{"id": "claude-opus-4-8"}`. All Claude 4.5-family and later models are supported. | 
| `system` | A system prompt that defines the agent's behavior and persona. The system prompt is distinct from user messages, which should describe the work to be done. | 
| `tools` | The tools available to the agent. Combines pre-built agent tools, MCP tools, and custom tools. | 
| `mcp_servers` | MCP servers that provide standardized third-party capabilities. | 
| `skills` | Skills that supply domain-specific context with progressive disclosure. | 
| `multiagent` | A coordinator declaration listing the agents this agent can delegate to. See Multi-agent sessions. | 
| `description` | A description of what the agent does. | 
| `metadata` | Arbitrary key-value pairs for your own tracking. | 

You can also override `model`, `system`, `tools`, `mcp_servers`, and `skills` for a single session without changing the agent. See Override agent configuration for a session.

The following example defines a coding agent that uses Claude Opus 4.8 with access to the pre-built agent toolset. The toolset lets the agent write code, read files, search the web, and more. See the agent tools reference for the full list of supported tools.

The examples use curl, the `ant` CLI, or one of the SDKs. If you haven't set one up, the quickstart covers installation and client setup.

```
agent=$(ant beta:agents create \
  --name "Coding Assistant" \
  --model '{id: claude-opus-4-8}' \
  --system "You are a helpful coding agent." \
  --tool '{type: agent_toolset_20260401}' \
  --format json)
AGENT_ID=$(jq -r '.id' <<< "$agent")
AGENT_VERSION=$(jq -r '.version' <<< "$agent")
```
The response echoes your configuration and adds `id`, `type`, `version`, `created_at`, `updated_at`, and `archived_at` fields. The `version` starts at 1 and increments each time an update changes the agent.

```
{
  "id": "agent_01HqR2k7vXbZ9mNpL3wYcT8f",
  "type": "agent",
  "name": "Coding Assistant",
  "model": {
    "id": "claude-opus-4-8",
    "speed": "standard"
  },
  "system": "You are a helpful coding agent.",
  "description": null,
  "tools": [
    {
      "type": "agent_toolset_20260401",
      "default_config": {
        "permission_policy": { "type": "always_allow" }
      }
    }
  ],
  "skills": [],
  "mcp_servers": [],
  "metadata": {},
  "version": 1,
  "created_at": "2026-04-03T18:24:10.412Z",
  "updated_at": "2026-04-03T18:24:10.412Z",
  "archived_at": null
}
```
The `default_config` on the toolset shows its default permission policy, `always_allow`, which applies unless you configure one.

Updating an agent generates a new version when the configuration changes. The `version` field is required and must match the agent's current version, so you always update from a known state. A version mismatch returns a 409, and updates to archived agents are rejected.

```
ant beta:agents update \
  --agent-id "$AGENT_ID" \
  --version "$AGENT_VERSION" \
  --system "You are a helpful coding agent. Always write tests."
```
**Omitted fields are preserved.** You only need to include the fields you want to change.

**Scalar fields** (`model`, `system`, `name`, `description`) are replaced with the new value. `system` and `description` can be cleared by passing `null`. `model` and `name` are mandatory and cannot be cleared.

**Array fields** (`tools`, `mcp_servers`, `skills`) are fully replaced by the new array. To clear an array field entirely, pass `null` or an empty array.

** multiagent** is replaced as a whole, including its 

`agents` roster. Pass `null` to clear it.**Metadata** is merged at the key level. Keys you provide are added or updated. Keys you omit are preserved. To delete a specific key, set its value to `null`.

**No-op detection.** If the update produces no change relative to the current version, no new version is created and the existing version is returned.

**Coordinator rosters are not updated.** Coordinators that reference this agent in their `multiagent.agents` roster keep the version that was pinned when the coordinator was created or last updated, even if the reference omits `version`. To delegate to the new version, update the coordinator so its roster references it.

| Operation | Behavior | 
|---|---|
| Update | Generates a new agent version when the configuration changes. | 
| List versions | Returns the full version history so you can track changes over time. | 
| Archive | Makes the agent read-only. New sessions cannot reference it, but existing sessions continue to run. | 

Fetch the full version history to track how an agent has changed over time. Results are paginated, and the SDK examples fetch every page automatically.

`ant beta:agents:versions list --agent-id "$AGENT_ID"`Archiving makes the agent read-only and cannot be undone. Existing sessions continue to run, but new sessions cannot reference the agent. The response sets `archived_at` to the archive timestamp.

`ant beta:agents archive --agent-id "$AGENT_ID"`Configure tools available to your agent.

Attach reusable, filesystem-based expertise to your agent for domain-specific workflows.

Create a session to run your agent and begin executing tasks.

Event types, self-hosted worker CLI flags, supported MCP server types, rate limits, and branding guidelines for Claude Managed Agents.

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

- Source: [https://platform.claude.com/docs/en/managed-agents/agent-setup](https://platform.claude.com/docs/en/managed-agents/agent-setup)
