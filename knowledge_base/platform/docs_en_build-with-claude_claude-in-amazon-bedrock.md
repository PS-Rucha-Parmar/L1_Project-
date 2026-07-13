---
title: "Claude in Amazon Bedrock - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock"
library: "platform"
created: "2026-07-13T07:41:54.817725+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This guide walks you through setting up and making API calls to Claude in Amazon Bedrock. Claude in Amazon Bedrock runs on AWS-managed infrastructure with zero operator access (Anthropic personnel have no access to the inference infrastructure), letting you build sensitive applications entirely inside the AWS security boundary while using the same Messages API shape you use with Anthropic's first-party API.

This page covers Claude in Amazon Bedrock, which serves Claude through the Messages API at `/anthropic/v1/messages` on AWS-managed infrastructure. The previous Amazon Bedrock integration (the `InvokeModel` and `Converse` APIs with ARN-versioned model identifiers) remains available and is documented at Claude on Amazon Bedrock (legacy). For an Anthropic-operated alternative on AWS with AWS Marketplace billing and typically same-day feature access, see Claude Platform on AWS.

Claude Fable 5, Claude Opus 4.8, Claude Sonnet 5, Claude Opus 4.7, and Claude Haiku 4.5 are open to all Amazon Bedrock customers. Claude Mythos Preview requires an invitation; see Project Glasswing. For region availability, see Regions.

Before you begin, ensure you have:

Claude Mythos Preview additionally requires a dedicated AWS account that has been allowlisted by the Bedrock Marketplace team. Your Anthropic account executive can submit your account ID for allowlisting (typically processed within 24 hours), and AWS sends a welcome email once it's complete.

Claude in Amazon Bedrock supports three authentication paths. Choose the one that best fits your security requirements.

Use a Bedrock service role with AWS-managed keys for the most secure, long-lived access:

Admin: provision the service role

An AWS administrator provisions a Bedrock service role and grants developers `iam:PassRole` permission on the service role ARN.

Developer: pass the role

When calling the API, Bedrock assumes the service role on your behalf. See the Amazon Bedrock documentation for how to associate the role with your requests.

For identity-federated access with a 12-hour maximum session:

Admin: configure the IAM role

Create an IAM role scoped to your Claude models. The trust policy names your identity provider (SAML, OIDC, or AWS Identity Center). The permissions policy grants `bedrock-mantle:CreateInference` only on the allowed model ARNs.

Developer: authenticate and assume

Authenticate through your corporate identity provider, then assume the IAM role. AWS STS issues temporary credentials that the SDK or CLI uses to sign requests.

For short-term access without IAM roles (12-hour maximum, least preferred):

Admin: restrict token types

Block long-term keys by attaching a policy that denies `bedrock:CallWithBearerToken` unless the `bedrock:BearerTokenType` condition matches a short-term token.

Developer: mint a token

Use the `aws-bedrock-token-generator` CLI to mint a bearer token. Pass it in the `x-api-key` header on each request.

Anthropic's client SDKs support Claude in Amazon Bedrock through a Bedrock-specific package or module.

The endpoint follows the pattern `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages`. Unlike the `InvokeModel`-based integration, this endpoint uses standard SSE streaming and the same request body shape as Anthropic's first-party API.

The SDK resolves credentials and region using the standard AWS precedence: constructor arguments, then environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`), then the AWS config file and credential chain (SSO, assumed roles, ECS task role, IMDS).

You can also use the standard `Anthropic` client: set `base_url` to `https://bedrock-mantle.{region}.api.aws/anthropic` and pass your bearer token as `api_key`. This path supports bearer-token authentication only. SigV4 signing requires the dedicated client.

Model IDs in Claude in Amazon Bedrock carry an `anthropic.` provider prefix. Model capabilities and behaviors are documented on the Models overview page.

| Model | Model ID | Access | 
|---|---|---|
| Claude Fable 5 | anthropic.claude-fable-5 | Open | 
| Claude Opus 4.8 | anthropic.claude-opus-4-8 | Open | 
| Claude Opus 4.7 | anthropic.claude-opus-4-7 | Open | 
| Claude Sonnet 5 | `anthropic.claude-sonnet-5` | Open | 
| Claude Haiku 4.5 | anthropic.claude-haiku-4-5 | Open | 
| Claude Mythos Preview | anthropic.claude-mythos-preview | Invitation only (Project Glasswing) | 

Upgrading to a newer Claude model? In Claude Code, run `/claude-api migrate` to apply model ID swaps and breaking parameter changes across your codebase. The skill detects which cloud platform your code targets and adjusts model ID formats and feature changes for that platform. See Migrating to a newer Claude model.

For the full feature list with Amazon Bedrock availability, see Features overview.

`/anthropic/v1/messages`)`fallbacks` parameter; use the client-side fallback pattern instead)Claude in Amazon Bedrock is available in the following AWS regions. Amazon Bedrock offers two endpoint types:

The global endpoint is available for Claude Fable 5, Claude Opus 4.8, Claude Opus 4.7, Claude Sonnet 5, and Claude Haiku 4.5. Claude Mythos Preview is regional only and is available in `us-east-1`.

| AWS region | Location | Endpoint types | 
|---|---|---|
| `af-south-1` | Africa (Cape Town) | Global | 
| `ap-northeast-1` | Asia Pacific (Tokyo) | Global, JP, In-region only | 
| `ap-northeast-2` | Asia Pacific (Seoul) | Global | 
| `ap-northeast-3` | Asia Pacific (Osaka) | Global, JP | 
| `ap-south-1` | Asia Pacific (Mumbai) | Global | 
| `ap-south-2` | Asia Pacific (Hyderabad) | Global | 
| `ap-southeast-1` | Asia Pacific (Singapore) | Global | 
| `ap-southeast-2` | Asia Pacific (Sydney) | Global, AU | 
| `ap-southeast-3` | Asia Pacific (Jakarta) | Global | 
| `ap-southeast-4` | Asia Pacific (Melbourne) | Global, AU, In-region only | 
| `ca-central-1` | Canada (Central) | Global, US | 
| `ca-west-1` | Canada West (Calgary) | Global | 
| `eu-central-1` | Europe (Frankfurt) | Global, EU | 
| `eu-central-2` | Europe (Zurich) | Global, EU | 
| `eu-north-1` | Europe (Stockholm) | Global, EU, In-region only | 
| `eu-south-1` | Europe (Milan) | Global, EU | 
| `eu-south-2` | Europe (Spain) | Global, EU | 
| `eu-west-1` | Europe (Ireland) | Global, EU, In-region only | 
| `eu-west-2` | Europe (London) | Global, EU | 
| `eu-west-3` | Europe (Paris) | Global, EU | 
| `il-central-1` | Israel (Tel Aviv) | Global | 
| `me-central-1` | Middle East (UAE) | Global | 
| `sa-east-1` | South America (São Paulo) | Global | 
| `us-east-1` | US East (N. Virginia) | Global, US, In-region only | 
| `us-east-2` | US East (Ohio) | Global, US, In-region only | 
| `us-west-1` | US West (N. California) | Global, US | 
| `us-west-2` | US West (Oregon) | Global, US, In-region only | 

Default quota is 2 million input tokens per minute (TPM). You can request up to 4 million input TPM without additional Anthropic approval. AWS enforces requests-per-minute (RPM) limits on the Bedrock side; contact AWS support for RPM adjustments.

Data handling for this offering is governed by Amazon Bedrock. For details, see Data protection in Amazon Bedrock.

Claude in Amazon Bedrock emits logs to both CloudWatch and CloudTrail. Anthropic recommends retaining activity logs on at least a 30-day rolling basis to understand usage patterns and investigate potential issues.

For support, contact **[email protected]**. Include your AWS account ID and the `request-id` from any failed API responses.

**Claude Mythos Preview** is a research preview model available to invited customers on Amazon Bedrock. For more information, see Project Glasswing.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)
