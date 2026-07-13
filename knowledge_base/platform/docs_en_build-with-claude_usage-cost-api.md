---
title: "Usage and Cost API - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/usage-cost-api"
library: "platform"
created: "2026-07-13T07:52:24.983291+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

**The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.

The Usage & Cost Admin API provides programmatic and granular access to historical API usage and cost data for your organization. This data is similar to the information available in the Usage and Cost pages of the Claude Console.

This API enables you to better monitor, analyze, and optimize your Claude implementations:

**Admin API key required.** These endpoints require an Admin API key, which is different from a standard Claude API key. See Create an Admin API key to find where to create one for your organization type and which scopes to select.

Claude Enterprise organizations use an Analytics API key with a different API instead; see Which API do you need?.

**Claude Platform on AWS:** The programmatic Usage and Cost API endpoints are not currently available. View usage and cost data on the **Usage** and **Cost** pages in the Claude Console instead.

Anthropic provides cost and usage reporting through two APIs, depending on which Claude product your organization manages:

| Your organization | API | Key type | 
|---|---|---|
| Claude Console (Claude Platform) | The Usage and Cost Admin API described on this page | Admin API key ( `sk-ant-admin01-...`) | 
| Claude Enterprise (claude.ai) | The Claude Enterprise Analytics API cost and usage endpoints | Analytics API key | 

Claude Enterprise parent organizations do not appear in Claude Console and carry no Admin API keys, so for them the Analytics API key is the only path to this data. See Analytics APIs for how to create each key type and which plans the Claude Enterprise cost data applies to.

Leading observability platforms offer ready-to-use integrations for monitoring your Claude API usage and cost, without writing custom code. These integrations provide dashboards, alerting, and analytics to help you manage your API usage effectively.

Cloud intelligence platform for tracking and forecasting costs

LLM Observability with automatic tracing and monitoring

Agentless integration for easy LLM observability with out-of-the-box dashboards and alerts

Advanced querying and visualization through OpenTelemetry

FinOps platform for LLM cost & usage observability

Get your organization's daily usage for the last 7 days:

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-08T00:00:00Z&\
ending_at=2025-01-15T00:00:00Z&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
**Set a User-Agent header for integrations**

If you're building an integration, set your User-Agent header to help us understand usage patterns:

`User-Agent: YourApp/1.0.0 (https://yourapp.com)`Track token consumption across your organization with detailed breakdowns by model, workspace, and service tier with the `/v1/organizations/usage_report/messages` endpoint.

`1m`, `1h`, or `1d`)For complete parameter details and response schemas, see the Usage API reference.

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-15T00:00:00Z&\
ending_at=2025-01-15T23:59:59Z&\
models[]=claude-opus-4-8&\
service_tiers[]=batch&\
context_window[]=0-200k&\
bucket_width=1h" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
api_key_ids[]=apikey_01Rj2N8SVvo6BePZj99NhmiT&\
api_key_ids[]=apikey_01ABC123DEF456GHI789JKL&\
workspace_ids[]=wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ&\
workspace_ids[]=wrkspc_01XYZ789ABC123DEF456MNO&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
To retrieve your organization's API key IDs, use the List API Keys endpoint.

To retrieve your organization's workspace IDs, use the List Workspaces endpoint, or find your organization's workspace IDs in the Claude Console.

Track your data residency controls by grouping and filtering usage with the `inference_geo` dimension. This is useful for verifying geographic routing across your organization.

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
group_by[]=inference_geo&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
You can also filter to a specific geo. Valid values are `global`, `us`, and `not_available`:

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
inference_geos[]=us&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Models released before February 2026 (prior to Claude Opus 4.6 and Claude Sonnet 4.6) don't support the `inference_geo` request parameter, so their usage reports return `"not_available"` for this dimension. You can use `not_available` as a filter value in `inference_geos[]` to target those models.

Track fast mode usage by grouping and filtering with the `speed` dimension. This is useful for monitoring standard vs. fast mode usage.

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
group_by[]=speed&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: fast-mode-2026-02-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
You can also filter to a specific speed. Valid values are `standard` and `fast`:

```
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
speeds[]=fast&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: fast-mode-2026-02-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Both the `speeds[]` filter and the `speed` group_by value require the `fast-mode-2026-02-01` beta header.

| Granularity | Default Limit | Maximum Limit | Use Case | 
|---|---|---|---|
| `1m` | 60 buckets | 1440 buckets | Real-time monitoring | 
| `1h` | 24 buckets | 168 buckets | Daily patterns | 
| `1d` | 7 buckets | 31 buckets | Weekly/monthly reports | 

Retrieve service-level cost breakdowns in USD with the `/v1/organizations/cost_report` endpoint.

`description`, responses include parsed fields like `model` and `inference_geo``1d`)For complete parameter details and response schemas, see the Cost API reference.

Priority Tier costs use a different billing model and are not included in the cost endpoint. Track Priority Tier usage through the usage endpoint instead.

```
curl "https://api.anthropic.com/v1/organizations/cost_report?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
group_by[]=workspace_id&\
group_by[]=description" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Both endpoints support pagination for large datasets:

`has_more` is `true`, use the `next_page` value in your next request`has_more` is `false````
# First request
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
# Response includes: "has_more": true, "next_page": "page_xyz..."
# Next request with pagination
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7&\
page=page_xyz..." \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```
Explore detailed implementations in Claude Cookbook:

Usage and cost data typically appears within 5 minutes of API request completion, though delays may occasionally be longer.

The API supports polling once per minute for sustained use. For short bursts (e.g., downloading paginated data), more frequent polling is acceptable. Cache results for dashboards that need frequent updates.

Code execution costs appear in the cost endpoint grouped under `Code Execution Usage` in the description field. Code execution is not included in the usage endpoint.

Filter or group by `service_tier` in the usage endpoint and look for the `priority` value. Priority Tier costs are not available in the cost endpoint.

API usage from the Workbench is not associated with an API key, so `api_key_id` will be `null` even when grouping by that dimension.

Usage and costs attributed to the default workspace have a `null` value for `workspace_id`.

Use the Claude Code Analytics API, which provides per-user estimated costs and productivity metrics without the performance limitations of breaking down costs by many API keys. For general API usage with many keys, use the Usage API to track token consumption as a cost proxy.

The Usage and Cost APIs can be used to help you deliver a better experience for your users, help you manage costs, and preserve your rate limit. Learn more about some of these other features:

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/usage-cost-api](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api)
