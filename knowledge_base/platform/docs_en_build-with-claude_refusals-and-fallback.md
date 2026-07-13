---
title: "Refusals and fallback - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback"
library: "platform"
created: "2026-07-13T07:57:08.255269+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Claude Fable 5 includes safety classifiers that can decline a request. When that happens, you receive a normal response, not an error, with `stop_reason: "refusal"`. You can usually still get an answer by sending the same request to another Claude model. This page shows you how to recognize a refusal and how to set up that retry.

Read this page when you build on Claude Fable 5 and want declined requests to fall through to another model automatically. It also applies when you have just seen `"refusal"` in a response and want to know what to do next.

Related pages:

`stop_reason` values.The simplest setup: name a fallback model on the request, and the API handles the retry.

```
client = Anthropic()
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    fallbacks=[{"model": "claude-opus-4-8"}],
    betas=["server-side-fallback-2026-06-01"],
)
print(response.model)
```
The sections below cover what a refusal response contains, when to use server-side or client-side fallback, and how each is billed.

A refusal is a successful HTTP 200 response with `stop_reason: "refusal"`:

```
{
  "id": "msg_01XFUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "model": "claude-fable-5",
  "content": [],
  "stop_reason": "refusal",
  "stop_details": {
    "type": "refusal",
    "category": "cyber",
    "explanation": "This request was declined because it could enable cyber harm."
  },
  "usage": {
    "input_tokens": 412,
    "output_tokens": 0
  }
}
```
The `stop_details` object explains the decline:

`category`:`explanation`:`null` when the refusal does not map to a named category. That `null` is a normal, permanent value, not a placeholder.`stop_details` itself is `null` for every stop reason other than `refusal`.| `category` | What it means | 
|---|---|
| `"cyber"` | The request could enable cyber harm, such as malware or exploit development. Benign cybersecurity work can also trigger this category. | 
| `"bio"` | The request could enable biological harm, such as dangerous lab methods. Beneficial life sciences work can also trigger this category. | 
| `"frontier_llm"` | The request could assist the development of competing AI models, which is restricted under Anthropic's commercial terms. Benign machine learning work can also trigger this category. | 
| `"reasoning_extraction"` | The request asks the model to reproduce its internal reasoning in the response text. To get reasoning in a structured form instead, use adaptive thinking. | 

A refusal can arrive before any output, or mid-stream after partial output. In either case, treat any partial output as incomplete and discard it.

**How refusals are billed:** You are not billed for a refusal that arrives before any output. `content` is empty, token counts appear in `usage` but are not charged, and the request does not count against rate limits. A mid-stream refusal bills the input tokens and the output already streamed at normal rates.

There are three ways to retry a refused request on another model. The right one depends on where you are running and how much control you need.

| Your situation | Use | Why | 
|---|---|---|
| Claude API or Claude Platform on AWS, simplest setup | Server-side fallback | One request, one response. The API handles the retry. | 
| Any platform, using an Anthropic SDK | The SDK middleware | Configure once on the client. Retries happen automatically. | 
| Raw HTTP or custom retry logic | Manual retry with fallback credit | Full control. Fallback credit keeps the cost down. | 

Server-side fallback and the SDK middleware apply fallback credit for you. You only need the Fallback credit page when you build the retry yourself.

Server-side fallback retries a refused request inside a single API call. You name up to three fallback models, and when Claude Fable 5 declines, the API runs the next model in the chain on the same request. You get back one response that names the model that answered, so your user gets an answer in one round trip.

Server-side fallback is in beta on the Claude API and Claude Platform on AWS. The `fallbacks` parameter is rejected on the Message Batches API and is not available on Amazon Bedrock, Google Cloud, or Microsoft Foundry. On those platforms, use the SDK middleware instead.

Name the fallback models in the `fallbacks` parameter and send the `server-side-fallback-2026-06-01` beta header.

```
client = Anthropic()
response = client.beta.messages.create(
    model="claude-fable-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    fallbacks=[{"model": "claude-opus-4-8"}],
    betas=["server-side-fallback-2026-06-01"],
)
# A fallback_message entry in usage.iterations means a fallback model ran;
# pair it with stop_reason to confirm the fallback served the response.
fallback_ran = any(
    iteration.type == "fallback_message"
    for iteration in response.usage.iterations or []
)
served_by_fallback = fallback_ran and response.stop_reason != "refusal"
print(
    json.dumps(
        {
            "stop_reason": response.stop_reason,
            "model": response.model,
            "served_by_fallback": served_by_fallback,
        }
    )
)
```
A few rules apply to the `fallbacks` list:

`allowed_fallback_models` on the model's entry in the Models API.`model` and can override `max_tokens` and `thinking` for that attempt only.The beta header must carry exactly the date `2026-06-01`. Under any other `server-side-fallback-*` value, the `fallbacks` parameter is rejected with a 400 error. If you built against an earlier preview of this feature, update the beta header and the request and response shapes together to the ones on this page.

The response looks like any other message, with two additions:

`model` field reports the model that produced the returned message, whether that is the requested model or a fallback.`fallback` content block marks each point in `content` where one model's output gives way to the next: `{"type": "fallback", "from": {"model": ...}, "to": {"model": ...}}`.
`from.model` echoes the model string you sent when the declining hop is the requested model.`to.model` is always the resolved ID of the model that continues.On a refusal before any output, the `fallback` block is the first content block:

```
{
  "id": "msg_01XFUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-4-8",
  "content": [
    {
      "type": "fallback",
      "from": { "model": "claude-fable-5" },
      "to": { "model": "claude-opus-4-8" }
    },
    { "type": "text", "text": "Hi! How can I help you today?" }
  ],
  "stop_reason": "end_turn",
  "stop_details": null,
  "usage": {
    "input_tokens": 412,
    "output_tokens": 264,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 0,
    "iterations": [
      {
        "type": "message",
        "model": "claude-fable-5",
        "input_tokens": 535,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0
      },
      {
        "type": "fallback_message",
        "model": "claude-opus-4-8",
        "input_tokens": 412,
        "output_tokens": 264,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0
      }
    ]
  }
}
```
The `usage.iterations` array records every attempt. A model that declined appears as an ordinary `message` entry, and the model that served the turn appears as a `fallback_message` entry. If every model in the chain declines, the response is the last model's refusal, with a `message` entry for each earlier hop and a `fallback_message` entry for the last.

On the next turn, send the assistant content back as you received it. After a mid-output fallback, `content` can include block types the declining model produced before the handoff; the table below covers which to keep and which to drop when you echo the turn.

| Block type | On the next turn | 
|---|---|
| `fallback` | Keep it exactly where it appeared. The API uses its position to validate the thinking blocks around it, so a request that echoes thinking blocks from both sides of the boundary is rejected if the block is omitted or moved. | 
| `text` | Keep. | 
| Any block after the final `fallback`block | Keep. | 
| `thinking`,`redacted_thinking`, or`connector_text`before the final`fallback`block | Drop. | 
| Client-side `tool_use`before the final`fallback`block | Drop. | 
| `server_tool_use`before the final`fallback`block | Keep when paired with its result. Drop when it has no matching result. | 

A `connector_text` block carries narration text that some tool-using responses include between tool calls.

On a streaming request, the retry happens on the same stream, and nothing you have already received is invalidated. What you see depends on when the decline happens.

**When the decline happens before any output:**

`message_start` names the fallback model, and the `fallback` block is the first content block.`message_start` waits for the fallback attempt to start, time to first byte includes the declined attempt.**When the decline happens mid-output:**

`fallback` block (an ordinary `content_block_start` and `content_block_stop` pair with no deltas) marks the boundary.`text` blocks are passed to the fallback model as context; other block types remain in `content`.`message_start` already named the requested model, so read the serving model from the `fallback` block's `to.model` and from the `fallback_message` entry in the final `message_delta`'s `usage.iterations`.On a non-streaming request, a mid-output decline behaves differently: the response omits the declined model's partial output, and the fallback model answers from scratch. The result looks like a decline before any output, with the `fallback` block first. The declined attempt and its output tokens still appear in `usage.iterations`.

**Declines after server tools run:** when a decline fires after server tools (for example, web search or code execution) have already executed within a request, the API returns the refusal instead of advancing to a fallback model. If the `fallback-credit-2026-06-01` header is also set, that refusal carries a credit token redeemable by continuing the partial response, so the completed tool work is not lost. This applies only to server tools iterating within a single request. Conversations that use client-side tools fall back normally.

Every Anthropic SDK includes a refusal-fallback middleware. You configure it once on the client with your list of fallback models. Calls through `client.beta.messages` then retry refused requests automatically, on any platform. The middleware also sends the `fallback-credit-2026-06-01` beta header on every request it handles, so retries are repriced without per-request setup.

Pass the middleware to the client constructor, and share one `BetaFallbackState` instance across the requests of a conversation.

```
# On a refusal, the middleware retries on the listed fallback model and
# automatically sends the fallback-credit beta header on every request it handles.
client = Anthropic(
    middleware=[BetaRefusalFallbackMiddleware([{"model": "claude-opus-4-8"}])],
)
state = BetaFallbackState()  # pins follow-ups to the model that accepted
# Streaming: on a refusal the middleware retries on the fallback model and
# splices its events onto the open stream.
with (
    state,
    client.beta.messages.stream(
        max_tokens=1024,
        model="claude-fable-5",
        messages=[{"role": "user", "content": "Hello, Claude"}],
    ) as stream,
):
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final_message = stream.get_final_message()
print(f"\nserved by: {final_message.model}")
# Non-streaming: reusing the state keeps the conversation pinned.
with state:
    message = client.beta.messages.create(
        max_tokens=1024,
        model="claude-fable-5",
        messages=[{"role": "user", "content": "Hello, Claude"}],
    )
print(f"served by: {message.model}")
```
`fallback` content block at each model boundary, the same as server-side fallback responses. The middleware manages those blocks for you on later requests.`BetaFallbackState`, so follow-up requests that share the state stay pinned to it rather than re-asking a model that refused.The middleware and the server-side `fallbacks` parameter do the same job. Configure one or the other, never both on the same request. To send a server-side `fallbacks` request from an application that installs the middleware, use a separate client instance without it.

A refused request in a Message Batch comes back as `result.type: "succeeded"` with `stop_reason: "refusal"`. The `stop_details` field may be `null` on batch results, so detect refusals by checking `stop_reason` directly.

Server-side fallback is not available for batches (a batch request that includes `fallbacks` produces a per-item errored result). To retry refused batch items:

`fallbacks` parameter does not propagate into model calls made from inside tool execution.`fallback_message` entry in `usage.iterations` marks the latter), then alert on the gap between the two counts.`stop_reason`, not on `stop_details` or `content`.`stop_details` is informational and can be `null` on a refusal. Check for `stop_reason` equal to `"refusal"` directly.Avoid paying the prompt-cache cost twice when you build the retry yourself.

Every `stop_reason` value and how to handle it.

How SDK middleware works, including the refusal-fallback helper.

Move an existing application to Claude Fable 5.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback)
