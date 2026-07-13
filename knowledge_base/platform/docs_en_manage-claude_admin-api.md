---
title: "Admin API - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/manage-claude/admin-api"
library: "platform"
created: "2026-07-13T07:36:07.728228+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

`org:admin` OAuth token.**The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.

The Admin API allows you to programmatically manage your organization's resources, including organization members, workspaces, and API keys. This provides programmatic control over administrative tasks that would otherwise require manual configuration in the Claude Console.

**The Admin API requires special access**

The Admin API accepts two credentials: an Admin API key (starting with `sk-ant-admin...`) sent in the `x-api-key` header or an OAuth bearer token with the `org:admin` scope sent in the `authorization: Bearer` header. Only organization members with the admin role can provision Admin API keys, and only members with the admin, owner, or primary owner role can obtain `org:admin` tokens. See Create an Admin API key.

**Claude Platform on AWS:** Most of the Admin API is not available on Claude Platform on AWS. Workspace endpoints (create, get, list, update, and archive on `/v1/organizations/workspaces`) are available. Other endpoints including organization members, workspace members, invites, API keys, usage reports, cost reports, and rate limit reports are not available. See Claude Platform on AWS for details.

Authenticate with either credential. To create an Admin API key for your organization type, see Create an Admin API key. The following examples call the organization info endpoint both ways:

**OAuth bearer:**

```
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "authorization: Bearer $ANTHROPIC_OAUTH_TOKEN"
```
An `org:admin` token grants access to the whole organization, regardless of the workspace the underlying profile or federation rule is bound to. To obtain one, see the prerequisites in Manage WIF with the Admin API.

**Admin API key:**

```
curl --fail-with-body -sS "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
When you use the Admin API:

`org:admin` OAuth token; Admin API keys are not accepted)This is useful for:

There are five organization-level roles. See more details in the API Console roles and permissions article.

| Role | Permissions | 
|---|---|
| user | Can use Workbench | 
| claude_code_user | Can use Workbench and Claude Code | 
| developer | Can use Workbench and manage API keys | 
| billing | Can use Workbench and manage billing details | 
| admin | Can do all of the preceding, plus manage users | 

Organization owners and primary owners have all admin permissions and can additionally manage admins. All references to the admin role on this page also apply to owners and primary owners.

You can list organization members, update member roles, and remove members.

```
# List organization members
curl "https://api.anthropic.com/v1/organizations/users?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Update member role
curl "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"role": "developer"}'
# Remove member
curl --request DELETE "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
You can invite users to organizations and manage those invites.

```
# Create invite
curl --request POST "https://api.anthropic.com/v1/organizations/invites" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "email": "[email protected]",
    "role": "developer"
  }'
# List invites
curl "https://api.anthropic.com/v1/organizations/invites?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Delete invite
curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/{invite_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
For a comprehensive guide to workspaces, including Console and API examples, see Workspaces.

Manage user access to specific workspaces:

```
# Add member to workspace
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "user_id": "user_xxx",
    "workspace_role": "workspace_developer"
  }'
# List workspace members
curl "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Update member role
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "workspace_role": "workspace_admin"
  }'
# Remove member from workspace
curl --request DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Monitor and manage API keys. Each key in the response includes its `expires_at` timestamp (`null` for keys without an expiration):

```
# List API keys
curl "https://api.anthropic.com/v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Update API key
curl --request POST "https://api.anthropic.com/v1/organizations/api_keys/{api_key_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "status": "inactive",
    "name": "New Key Name"
  }'
```
Create and manage service accounts (`svac_...`), the non-human identities that Workload Identity Federation tokens act as. Admin API keys are not accepted on the service-account, federation-issuer, or federation-rule endpoints; use an `org:admin` OAuth token. See Manage WIF with the Admin API.

Register the OIDC identity providers (`fdis_...`) whose tokens may assert workload identity for your organization. See Manage WIF with the Admin API.

Manage the rules (`fdrl_...`) that map issuer tokens to service accounts and scopes. See Manage WIF with the Admin API.

Get information about your organization programmatically with the `/v1/organizations/me` endpoint.

For example:

```
curl "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
```
{
  "id": "12345678-1234-5678-1234-567812345678",
  "type": "organization",
  "name": "Organization Name"
}
```
This endpoint is useful for programmatically determining which organization an Admin API key belongs to.

For complete parameter details and response schemas, see the Organization Info API reference.

Track your organization's usage and costs with the Usage and Cost API.

Monitor developer productivity and Claude Code adoption with the Claude Code Analytics API.

Read the rate limits configured for your organization and its workspaces with the Rate Limits API.

Retrieve audit and activity data for your organization with the Compliance API. Admin API keys can read the Activity Feed only; for full access, see Set up the Compliance API.

To effectively use the Admin API:

`expires_at`, and rotate keys periodicallyFor workspace-specific questions, see the Workspaces FAQ.

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

- Source: [https://platform.claude.com/docs/en/manage-claude/admin-api](https://platform.claude.com/docs/en/manage-claude/admin-api)
