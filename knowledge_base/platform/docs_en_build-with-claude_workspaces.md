---
title: "Workspaces - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/workspaces"
library: "platform"
created: "2026-07-13T07:51:50.944023+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Workspaces provide a way to organize your API usage within an organization. Use workspaces to separate different projects, environments, or teams while maintaining centralized billing and administration.

Every organization has a **Default Workspace** that cannot be renamed, archived, or deleted. When you create additional workspaces, you can assign API keys, members, and resource limits to each one.

Key characteristics:

`wrkspc_` prefix (for example, `wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ`)When a member of your organization first signs in to Claude Code with their Claude Console account, Anthropic automatically creates a **Claude Code** workspace in the organization and adds that member to it. Every subsequent member who signs in to Claude Code is added the same way.

The Claude Code workspace keeps Claude Code traffic separate from your other API workloads:

Archiving the Claude Code workspace disables Claude Code sign-in through Console billing for the whole organization.

Members can have different roles in each workspace, allowing fine-grained access control.

| Role | Permissions | 
|---|---|
| Workspace User | Use the Workbench only | 
| Workspace Limited Developer | Create and manage API keys, use the API. Cannot access session tracing views or download files. | 
| Workspace Developer | Create and manage API keys, use the API | 
| Workspace Admin | Full control over workspace settings and members | 
| Workspace Billing | View workspace billing information (inherited from organization billing role) | 

The Workspace Billing role cannot be manually assigned. It's inherited from having the organization billing role.

Only organization admins can create workspaces. Organization users and developers must be added to workspaces by an admin.

Create and manage workspaces in the Claude Console.

Open workspace settings

In the Claude Console, go to **Settings > Workspaces**.

Create a workspace

Click **Create workspace**.

Configure the workspace

Enter a workspace name and select a color for visual identification.

Create the workspace

Click **Create** to finalize.

To switch between workspaces in the Console, use the **Workspaces** selector in the top-left corner.

To modify a workspace's name or color:

The Default Workspace cannot be renamed or deleted.

To remove a member, click the trash icon next to their name.

Organization admins and billing members cannot be removed from workspaces while they hold those organization roles.

In the **Limits** tab, you can configure:

To archive a workspace, click the ellipsis menu (**...**) and select **Archive**. Archiving:

Archiving a workspace immediately revokes all API keys in that workspace. This action cannot be undone. If you archive the Claude Code workspace, members of your organization can no longer sign in to Claude Code through Console billing.

Programmatically manage workspaces using the Admin API.

Admin API endpoints require an Admin API key (starting with `sk-ant-admin...`) that differs from standard API keys. See Create an Admin API key for how to provision one.

```
# Create a workspace
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"name": "Production"}'
# List workspaces
curl "https://api.anthropic.com/v1/organizations/workspaces?limit=10&include_archived=false" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Archive a workspace
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/archive" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
For complete parameter details and response schemas, see the Workspaces API reference.

Add, update, or remove members from a workspace:

```
# Add a member to a workspace
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "user_id": "user_xxx",
    "workspace_role": "workspace_developer"
  }'
# Update a member's role
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"workspace_role": "workspace_admin"}'
# Remove a member from a workspace
curl --request DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
For complete parameter details, see the Workspace Members API reference.

API keys are scoped to a specific workspace. When you create an API key in a workspace, it can only access resources within that workspace.

Resources scoped to workspaces include:

Some resources cannot be managed with a workspace API key:

`workspace:manage_tunnels` OAuth token obtained through Workload Identity Federation, not a workspace API key. Tunnels are created in a workspace, and the Console Prompt caches are also isolated per workspace on the Claude API, Claude Platform on AWS, and Microsoft Foundry. On Amazon Bedrock and Google Cloud, prompt caches are isolated per organization.

To retrieve your organization's workspace IDs, use the List Workspaces endpoint, or find them in the Claude Console.

You can set custom spend and rate limits for each workspace to protect against overuse and ensure fair resource distribution.

Workspace limits can be set lower than (but not higher than) your organization's limits:

For detailed information on rate limits and how they work, see Rate limits. You can also read your current organization and workspace rate limits programmatically with the Rate Limits API.

Track usage and costs by workspace using the Usage and Cost API:

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
workspace_ids[]=wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ&\
group_by[]=workspace_id&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Usage and costs attributed to the Default Workspace have a `null` value for `workspace_id`.

Create separate workspaces for development, staging, and production:

| Workspace | Purpose | 
|---|---|
| Development | Testing and experimentation with lower rate limits | 
| Staging | Pre-production testing with production-like limits | 
| Production | Live traffic with full rate limits and monitoring | 

Assign workspaces to different teams for cost allocation and access control:

Create workspaces for specific projects or products to track usage and costs separately.

Plan your workspace structure

Consider how you'll organize workspaces before creating them. Think about billing, access control, and usage tracking needs.

Use meaningful names

Name workspaces clearly to indicate their purpose (for example, "Production - Customer Chatbot", "Dev - Internal Tools").

Set appropriate limits

Configure spend and rate limits to prevent unexpected costs and ensure fair resource distribution.

Audit access regularly

Review workspace membership periodically to ensure only appropriate users have access.

Monitor usage

Use the Usage and Cost API to track workspace-level consumption.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/workspaces](https://platform.claude.com/docs/en/build-with-claude/workspaces)
