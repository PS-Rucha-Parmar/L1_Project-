---
title: "Fast mode (research preview) - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/fast-mode"
library: "platform"
created: "2026-07-13T07:59:45.943863+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Fast mode delivers up to 2.5x higher output tokens per second from Claude Opus 4.8 and Claude Opus 4.7 at premium pricing. Set `speed: "fast"` with the `fast-mode-2026-02-01` beta header on your request to opt in.

Fast mode is in research preview. Contact your account manager to request access. If you do not have an account manager, join the waitlist for fast mode.

This feature is eligible for Zero Data Retention (ZDR). When your organization has a ZDR arrangement, data sent through this feature is not stored after the API response is returned.

Fast mode is supported on the following models:

Fast mode for Claude Opus 4.8 launches as a research preview on the Claude API, including Claude Managed Agents, only. It is not available on Amazon Bedrock, Google Cloud, or Microsoft Foundry.

Fast mode for Claude Opus 4.7 is deprecated as of June 25, 2026, and will be removed on July 24, 2026. After removal, requests to `claude-opus-4-7` with `speed: "fast"` will return an error; unlike Claude Opus 4.6 (see the following note), Claude Opus 4.7 does not fall back to standard speed. The model itself remains available at standard speed. To continue using fast mode, migrate to Claude Opus 4.8.

As of June 29, 2026, fast mode is not available on Claude Opus 4.6. Requests to `claude-opus-4-6` with `speed: "fast"` do not return an error: they run at standard speed and are billed at standard rates rather than fast mode's premium rates, and the response reports `usage.speed: "standard"`. To continue using fast mode, migrate to Claude Opus 4.8.

Fast mode runs the same model with a faster inference configuration. There is no change to intelligence or capabilities.

```
client = anthropic.Anthropic()
response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    speed="fast",
    betas=["fast-mode-2026-02-01"],
    messages=[
        {"role": "user", "content": "Refactor this module to use dependency injection"}
    ],
)
print(response.content[0].text)
```
Fast mode is priced at a per-model multiplier on standard rates across the full context window, including requests over 200k input tokens. The following table shows fast mode pricing for each supported model:

| Model | Input | Output | 
|---|---|---|
| Claude Opus 4.8 | $10 / MTok | $50 / MTok | 
| Claude Opus 4.7 | $30 / MTok | $150 / MTok | 

Fast mode pricing stacks with other pricing modifiers:

For complete pricing details, see the pricing page.

Fast mode has a dedicated rate limit that is separate from standard Opus rate limits. When your fast mode rate limit is exceeded, the API returns a `429` error with a `retry-after` header indicating when capacity will be available.

The response includes headers that indicate your fast mode rate limit status:

| Header | Description | 
|---|---|
| `anthropic-fast-input-tokens-limit` | Maximum fast mode input tokens per minute | 
| `anthropic-fast-input-tokens-remaining` | Remaining fast mode input tokens | 
| `anthropic-fast-input-tokens-reset` | Time when the fast mode input token limit resets | 
| `anthropic-fast-output-tokens-limit` | Maximum fast mode output tokens per minute | 
| `anthropic-fast-output-tokens-remaining` | Remaining fast mode output tokens | 
| `anthropic-fast-output-tokens-reset` | Time when the fast mode output token limit resets | 

For tier-specific rate limits, see the rate limits page.

The response `usage` object includes a `speed` field that indicates which speed was used, either `"fast"` or `"standard"`. On supported models, fast mode doesn't silently fall back to standard speed on rate limits or capacity (you'll get a `429` or `529` instead), so when you request `speed: "fast"` on Claude Opus 4.8 or Claude Opus 4.7, `usage.speed` is `"fast"`. On Claude Opus 4.6, where fast mode is not available, requests with `speed: "fast"` run at standard speed and return `usage.speed: "standard"`. Check this field to confirm which speed served a request.

```
client = anthropic.Anthropic()
response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    speed="fast",
    betas=["fast-mode-2026-02-01"],
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.usage.speed)  # "fast" or "standard"
```
```
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "usage": {
    "input_tokens": 8,
    "output_tokens": 12,
    "speed": "fast"
  }
}
```
To track fast mode usage and costs across your organization, see the Usage and Cost API.

When fast mode rate limits are exceeded, the API returns a `429` error with a `retry-after` header. The Anthropic SDKs automatically retry these requests up to 2 times by default (configurable with `max_retries`), waiting for the server-specified delay before each retry. Because fast mode uses continuous token replenishment, the `retry-after` delay is typically short and requests succeed once capacity is available.

This section covers an opt-in client-side fallback when fast mode is rate limited. It is separate from the behavior on Claude Opus 4.6, where fast mode is not available and requests run at standard speed automatically.

If you'd prefer to fall back to standard speed rather than wait for fast mode capacity, catch the rate limit error and retry without `speed: "fast"`. Set `max_retries` to `0` on the initial fast request to skip automatic retries and fail immediately on rate limit errors.

Falling back from fast to standard speed will result in a prompt cache miss. Requests at different speeds do not share cached prefixes.

Because setting `max_retries` to `0` also disables retries for other transient errors (overloaded, internal server errors), the following examples reissue the original request with default retries for those cases.

```
client = anthropic.Anthropic()
def create_message_with_fast_fallback(max_retries=0, max_attempts=3, **params):
    try:
        return client.with_options(max_retries=max_retries).beta.messages.create(
            **params
        )
    except anthropic.RateLimitError:
        if params.get("speed") == "fast":
            del params["speed"]
            return create_message_with_fast_fallback(max_retries=max_retries, **params)
        raise
    except (
        anthropic.APIStatusError,
        anthropic.APIConnectionError,
    ) as error:
        if isinstance(error, anthropic.APIStatusError) and error.status_code < 500:
            raise
        if max_attempts > 1:
            return create_message_with_fast_fallback(
                max_retries=max_retries, max_attempts=max_attempts - 1, **params
            )
        raise
message = create_message_with_fast_fallback(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    betas=["fast-mode-2026-02-01"],
    speed="fast",
    max_retries=0,
)
```
`speed: "fast"` do not return an error: they run at standard speed and are billed at standard rates. On any other model, sending `speed: "fast"` returns an error.Get validated JSON results from agent workflows.

Learn about Anthropic's pricing structure for models and features.

Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency.

Stream Messages API responses incrementally with server-sent events, including text, tool use, and extended thinking deltas.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/fast-mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)
