---
title: "Streaming refusals - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals"
library: "platform"
created: "2026-07-13T08:01:19.737388+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Starting with Claude 4 models, streaming responses from Claude's API return ** stop_reason: "refusal"** when streaming classifiers intervene to handle potential policy violations. This safety feature helps maintain content compliance during real-time streaming.

This page covers how refusals appear in streaming responses. For every `stop_reason` value and how to handle it, see Stop reasons and fallback. To retry refused requests on another Claude model, see Refusals and fallback.

When streaming classifiers detect content that violates Anthropic's policies, the API returns this response:

```
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello.."
    }
  ],
  "stop_reason": "refusal",
  "stop_details": {
    "type": "refusal",
    "category": "cyber",
    "explanation": "This request was declined because it could enable cyber harm."
  }
}
```
In the event stream, `stop_details` arrives on the `message_delta` event alongside `stop_reason`.

A `refusal` response from streaming classifiers may include a `stop_details` object with a `category` and a human-readable `explanation` that you can surface to the user. See Refusals and fallback for the full response shape and the available categories.

`stop_details` (and its `category` / `explanation`) can be `null`, for example when the refusal maps to no named category, or on earlier models. Branch on `stop_reason` rather than assuming `stop_details` is populated, and provide your own user-facing messaging when it is `null`.

When you receive ** stop_reason: refusal**, you must reset the conversation context before continuing. You can remove or rephrase the turn that triggered the refusal, or clear the conversation history entirely. Attempting to continue without resetting will result in continued refusals.

Usage metrics are still provided in the response, even when the response is refused.

When a refusal arrives before Claude generates any output, you are not billed for the request on the Claude API, and the usage counts in that response are informational only. When Claude generates output before the refusal, you are billed for that request.

Resetting context is not the only way to recover. You can also retry the refused request on a different Claude model, and the Refusals and fallback page shows how to set that up with server-side fallback, the SDK middleware, or a manual retry.

Here's how to detect and handle streaming refusals in your application:

```
client = anthropic.Anthropic()
messages = []
def reset_conversation():
    """Reset conversation context after refusal"""
    global messages
    messages = []
    print("Conversation reset due to refusal")
try:
    with client.messages.stream(
        max_tokens=1024,
        messages=messages + [{"role": "user", "content": "Hello"}],
        model="claude-opus-4-8",
    ) as stream:
        for event in stream:
            # Check for refusal in message delta
            if event.type == "message_delta":
                if event.delta.stop_reason == "refusal":
                    reset_conversation()
                    break
except Exception as e:
    print(f"Error: {e}")
```
The API currently handles refusals in three different ways:

| Refusal Type | Response Format | When It Occurs | 
|---|---|---|
| Streaming classifier refusals | `stop_reason`:`refusal` | During streaming when content violates policies | 
| API input and copyright validation | 400 error codes | When input fails validation checks | 
| Model-generated refusals | Standard text responses | When the model itself decides to refuse | 

Future API versions will expand the ** stop_reason: refusal** pattern to unify refusal handling across all types.

`stop_reason`: `refusal`If you built refusal handling when this feature first shipped, or you're adding it to an existing integration, check the following:

`stop_reason`: `"refusal"`, so monitoring built only on error rates won't surface it. Track refusals as their own signal.`stop_details` object that identifies the policy category behind the decline. See Refusals and fallback for the full response shape.`stop_reason`: `"refusal"`, not as an errored result.`stop_reason`.`stop_reason`: `"refusal"`, so branch on the stop reason rather than on model-specific behavior.Retry refused requests on another Claude model, server-side or in your client.

Every `stop_reason` value and how to handle it.

Stream responses and read `stop_reason` from `message_delta` events as they arrive.

Serve users across languages with Claude's cross-lingual capabilities.

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

- Source: [https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals)
