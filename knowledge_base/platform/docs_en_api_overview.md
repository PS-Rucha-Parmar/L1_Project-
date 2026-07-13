---
title: "API overview - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/api/overview"
library: "platform"
created: "2026-07-13T07:36:39.384613+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

The Claude API is a RESTful API at `https://api.anthropic.com` that provides programmatic access to Claude models and Claude Managed Agents.

**New to Claude?** For direct model access, start with Get started and Working with Messages. For managed agent infrastructure, see the Claude Managed Agents quickstart.

To use the Claude API, you'll need:

For step-by-step setup instructions, see Get started.

The Claude API includes the following APIs:

**General Availability:**

`POST /v1/messages`)`POST /v1/messages/batches`)`POST /v1/messages/count_tokens`)`GET /v1/models`)**Beta:**

`POST /v1/files`, `GET /v1/files`)`POST /v1/skills`, `GET /v1/skills`)`POST /v1/agents`, `GET /v1/agents`)`POST /v1/sessions`, `GET /v1/sessions/{id}/stream`)`POST /v1/environments`, `GET /v1/environments`)For the complete API reference with all endpoints, parameters, and response schemas, explore the API reference pages listed in the navigation. To access beta features, see Beta headers.

For details on both authentication methods and when to use each, see Authentication. All requests to the Claude API must include these headers:

| Header | Value | Required | 
|---|---|---|
| `x-api-key` | Your API key from Console | One of `x-api-key`or`Authorization` | 
| `Authorization` | `Bearer <token>`, where`<token>`is a short-lived access token obtained from`POST /v1/oauth/token`through Workload Identity Federation | One of `x-api-key`or`Authorization` | 
| `anthropic-version` | API version (for example, `2023-06-01`) | Yes | 
| `content-type` | `application/json` | Yes | 

If you are using the Client SDKs, the SDK will send these headers automatically. For API versioning details, see API versions.

When accessing Claude through a cloud platform, authentication is integrated with the cloud provider's IAM system. See the platform-specific documentation for supported credential types, required headers, and authentication options.

The API is made available through the web Console. You can use the Workbench to try out the API in the browser and then generate API keys in Account Settings. You choose each key's expiration when you create it. Use workspaces to segment your API keys and control spend by use case.

Anthropic provides official SDKs that simplify API integration by handling authentication, request formatting, error handling, and more.

**Benefits:**

For a list of client SDKs, see Client SDKs.

Claude is available through the direct Claude API and through cloud platforms. Choose based on your infrastructure, feature availability, compliance requirements, and pricing preferences.

Access Claude through AWS, Google Cloud, or Microsoft Azure:

| Platform | Provider | Documentation | 
|---|---|---|
| Claude Platform on AWS | AWS (Anthropic-operated) | Claude Platform on AWS | 
| Amazon Bedrock | AWS | Claude in Amazon Bedrock | 
| Agent Platform | Google Cloud | Claude on Google Cloud | 
| Microsoft Foundry | Microsoft Azure (Anthropic-operated) | Claude in Microsoft Foundry | 

Claude Managed Agents is available through the direct Claude API and Claude Platform on AWS. For feature availability across platforms, see the Features overview.

| Endpoint | Maximum request size | 
|---|---|
| Messages, Token Counting | 32 MB | 
| Message Batches API | 256 MB | 
| Files API | 500 MB | 
| Sessions, Agents, Environments | 32 MB | 

If you exceed these limits, you'll receive a 413 `request_too_large` error.

Partner-operated platforms have their own request size limits: Google Cloud limits requests to 30 MB, and Bedrock limits requests to 20 MB. Claude Platform on AWS uses the same limits as the direct Claude API. Consult your platform's documentation for current values.

The Claude API includes the following headers in every response:

`request-id`: A globally unique identifier for the request`anthropic-organization-id`: The organization ID associated with the API key used in the requestClaude Platform on AWS adds an AWS request ID (`x-amzn-requestid`) alongside the standard `request-id` header. See Request IDs for the dual-ID handling pattern.

List endpoints return results in pages. Most newer list endpoints use the `page` and `next_page` cursor scheme described in this section. Some use a different scheme; see the note at the end of this section. Use the `limit` query parameter to control the page size and the `page` query parameter to fetch an adjacent page. Each response includes a `data` array alongside cursor fields for navigating between pages.

| Name | Location | Description | 
|---|---|---|
| `limit` | Query parameter | Maximum number of items to return per page. | 
| `page` | Query parameter | Opaque cursor from a previous response. Pass a `next_page`or`prev_page`value here to fetch the adjacent page. | 
| `order` | Query parameter | Sort direction for the results ( `asc`or`desc`), on list endpoints that support sorting. A`page`cursor is only valid with the`order`it was created with. | 
| `next_page` | Response field | Cursor for the next page, or `null`if there are no more results. | 
| `prev_page` | Response field | Cursor for the previous page on endpoints that support backward pagination (currently `GET /v1/sessions`), or`null`if you are on the first page. Other list endpoints omit the field. | 

To go back a page, pass `prev_page` as the `page` parameter. `prev_page` is `null` when you're on the first page. Not all list endpoints support `prev_page`. Only `GET /v1/sessions` returns `prev_page`; on list endpoints that do not support backward pagination, the field is absent from the response rather than `null`. For a request walkthrough, see Listing sessions.

Every SDK provides an auto-paginating iterator that follows `next_page` for you. In Python and TypeScript, you get it by iterating the list result directly. The other SDKs provide the iterator through a separate method. SDK auto-pagination is forward-only; to go back a page, read `prev_page` from the response and pass it back as the `page` parameter yourself. See client SDKs for language-specific details.

Some list endpoints use a different cursor scheme. The Message Batches API, the Files API, the Models API, and several Admin API endpoints take `after_id` and `before_id` query parameters instead of `page`. Their responses return `has_more`, `first_id`, and `last_id` instead of `next_page`. Some endpoints that use the `page` scheme, such as `GET /v1/skills`, also return a `has_more` Boolean alongside `next_page`. See the reference page for each endpoint for its exact pagination fields.

The API enforces rate limits and spend limits to prevent misuse and manage capacity. Limits are organized into usage tiers; your organization is placed on a tier automatically and can move to a higher tier over time. Each tier has:

You can view your organization's current limits in the Console. For higher limits, use **Request rate limit increase** on the Limits page.

For detailed information about limits, tiers, and the token bucket algorithm used for rate limiting, see Rate limits.

The Claude API is available in many countries and regions worldwide. Check the supported regions page to confirm availability in your location.

Complete API specification for direct model interactions

Agents, Sessions, and Environments endpoints

Python, TypeScript, C#, Go, Java, PHP, and Ruby

Usage tiers, requesting higher limits, and the token bucket algorithm

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

- Source: [https://platform.claude.com/docs/en/api/overview](https://platform.claude.com/docs/en/api/overview)
