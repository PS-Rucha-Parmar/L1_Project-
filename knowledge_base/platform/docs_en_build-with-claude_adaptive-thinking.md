---
title: "Adaptive thinking - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking"
library: "platform"
created: "2026-07-13T07:58:11.244198+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This feature is eligible for Zero Data Retention (ZDR). When your organization has a ZDR arrangement, data sent through this feature is not stored after the API response is returned.

Adaptive thinking is the recommended way to use extended thinking with Claude Opus 4.8, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, and Claude Sonnet 4.6, and the only thinking mode on Claude Fable 5 and Claude Mythos 5. Instead of manually setting a thinking token budget, adaptive thinking lets Claude dynamically determine when and how much to use extended thinking based on the complexity of each request. Per-model defaults and restrictions are listed under Supported models.

Adaptive thinking can drive better performance than extended thinking with a fixed `budget_tokens` for many workloads, especially workloads that mix trivial and complex requests, and long-horizon agentic workflows. No beta header is required.

If your workload requires predictable latency or precise control over thinking costs, extended thinking with `budget_tokens` is still functional on Claude Opus 4.6 and Claude Sonnet 4.6 but is deprecated and no longer recommended. See the deprecation warning in Supported models.

Adaptive thinking is supported on the following models:

`thinking: {type: "disabled"}` is not supported. Neither model is available under zero data retention.`thinking: {type: "disabled"}` is not supported, and manual `{type: "enabled", budget_tokens: N}` is still accepted.`thinking: {type: "adaptive"}` in your request; manual `thinking: {type: "enabled"}` is rejected with a 400 error.`thinking: {type: "adaptive"}` in your request; manual `thinking: {type: "enabled"}` is rejected with a 400 error.`thinking: {type: "adaptive"}`; manual `{type: "enabled", budget_tokens: N}` is still accepted but deprecated.`thinking: {type: "disabled"}` to turn it off. Manual `{type: "enabled"}` is rejected with a 400 error.`thinking: {type: "adaptive"}`; manual `{type: "enabled", budget_tokens: N}` is still accepted but deprecated.`thinking.type: "enabled"` and `budget_tokens` are **deprecated** on Opus 4.6 and Sonnet 4.6 and will be removed in a future model release. Use `thinking.type: "adaptive"` with the effort parameter instead. Existing `budget_tokens` configurations are still functional but no longer recommended; plan to migrate.

Older models, such as Claude Sonnet 4.5 and Claude Opus 4.5, do not support adaptive thinking and require `thinking.type: "enabled"` with `budget_tokens`.

In adaptive mode, thinking is optional for the model. Claude evaluates the complexity of each request and determines whether and how much to use extended thinking. At the default effort level (`high`), Claude almost always thinks. At lower effort levels, Claude may skip thinking for simpler problems.

Adaptive thinking also automatically enables interleaved thinking. This means Claude can think between tool calls, making it especially effective for agentic workflows.

Set `thinking.type` to `"adaptive"` in your API request. The examples also set `thinking.display` to `"summarized"` to make the thinking text visible: on the newest models `display` defaults to `"omitted"`, which returns thinking blocks with an empty `thinking` field. See Controlling thinking display for details.

```
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[
        {
            "role": "user",
            "content": "Explain why the sum of two even numbers is always even.",
        }
    ],
)
for block in response.content:
    if block.type == "thinking":
        print(f"\nThinking: {block.thinking}")
    elif block.type == "text":
        print(f"\nResponse: {block.text}")
```
Thinking tokens count toward `max_tokens`, so set it high enough to leave room for both thinking and the response text. See Cost control.

You can combine adaptive thinking with the effort parameter to guide how much thinking Claude does. The effort level acts as soft guidance for Claude's thinking allocation:

| Effort level | Thinking behavior | 
|---|---|
| `max` | Claude always thinks with no constraints on thinking depth. Available on all models that support adaptive thinking. | 
| `xhigh` | Claude always thinks deeply with extended exploration. Available on Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Opus 4.7, and Claude Sonnet 5. | 
| `high`(default) | Claude almost always thinks. Provides deep reasoning on complex tasks. | 
| `medium` | Claude uses moderate thinking. May skip thinking for simple queries. | 
| `low` | Claude minimizes thinking. Skips thinking for simple tasks where speed matters most. | 

```
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
for block in response.content:
    if block.type == "text":
        print(block.text)
```
Adaptive thinking works with streaming. Thinking blocks are streamed through `thinking_delta` events, the same as in manual thinking mode. As in the earlier examples, `thinking.display: "summarized"` makes the streamed thinking text visible:

```
client = anthropic.Anthropic()
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[
        {
            "role": "user",
            "content": "What is the greatest common divisor of 1071 and 462?",
        }
    ],
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            print(f"\nStarting {event.content_block.type} block...")
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
```
| Mode | Config | Availability | When to use | 
|---|---|---|---|
| Adaptive | `thinking: {type: "adaptive"}` | Claude Fable 5 (always on), Claude Mythos 5 (always on), Claude Mythos Preview (default), Claude Opus 4.8 (only mode), Claude Opus 4.7 (only mode), Claude Opus 4.6, Claude Sonnet 5 (default), and Claude Sonnet 4.6 | Claude determines when and how much to use extended thinking. Use `effort`to guide. | 
| Manual | `thinking: {type: "enabled", budget_tokens: N}` | All models except Claude Fable 5, Claude Mythos 5, Claude Sonnet 5, Claude Opus 4.8, and Claude Opus 4.7 (rejected with a 400 error). Deprecated on Opus 4.6 and Sonnet 4.6 (consider adaptive mode instead). | When you need precise control over thinking token spend. | 
| Disabled | `thinking: {type: "disabled"}` | All models except Claude Fable 5, Claude Mythos 5, and Claude Mythos Preview. On Claude Sonnet 5, pass `{type: "disabled"}`explicitly (omitting`thinking`defaults to adaptive). | When you don't need extended thinking and want the lowest latency. | 

Per-model defaults and restrictions are listed under Supported models. Models older than those listed accept only `type: "enabled"` with `budget_tokens`, when they support extended thinking at all.

**Interleaved thinking availability by mode:**

`interleaved-thinking-2025-05-14` beta header.When using adaptive thinking, previous assistant turns don't need to start with thinking blocks. This is more flexible than manual mode, where the API enforces that thinking-enabled turns begin with a thinking block.

Separately, Claude Fable 5, Claude Mythos 5, Claude Mythos Preview, Claude Opus 4.8, Claude Opus 4.7, and Claude Sonnet 5 reject non-default `temperature`, `top_p`, and `top_k` values with a 400 error. This applies to every request on these models, regardless of whether thinking is active.

Consecutive requests using `adaptive` thinking preserve prompt cache breakpoints. However, switching between `adaptive` and `enabled`/`disabled` thinking modes breaks cache breakpoints for messages. System prompts and tool definitions remain cached regardless of mode changes.

Adaptive thinking's triggering behavior is promptable. If Claude is thinking more or less often than you'd like, you can add guidance to your system prompt:

```
Extended thinking adds latency and should only be used when it
will meaningfully improve answer quality, typically for problems
that require multi-step reasoning. When in doubt, respond directly.
```
To encourage thinking instead, use a phrase like:

`This task involves multi-step reasoning. Think carefully before responding.`Steering effectiveness can be sensitive to exact wording. If one phrasing doesn't produce the behavior you want, try a more direct variant.

You can also steer thinking on a per-message basis from the user turn. Appending `"Please think hard before responding."` to a user message encourages Claude to think on that turn; `"Answer directly without deliberating."` suppresses it. This works independently of the system prompt and is useful when only some requests in a conversation warrant extended reasoning.

Steering Claude to think less often may reduce quality on tasks that benefit from reasoning. Measure the impact on your specific workloads before deploying prompt-based tuning to production. Consider testing with lower effort levels first.

Use `max_tokens` as a hard limit on total output (thinking + response text). The `effort` parameter provides additional soft guidance on how much thinking Claude allocates. Together, these give you effective control over cost.

At `high` and `max` effort levels, Claude may think more extensively and can be more likely to exhaust the `max_tokens` budget. If you observe `stop_reason: "max_tokens"` in responses, consider increasing `max_tokens` to give the model more room, or lowering the effort level.

The following concepts apply to all models that support extended thinking, regardless of whether you use adaptive or manual mode.

With extended thinking enabled, the Messages API for Claude 4 models returns a summary of Claude's full thinking process. Summarized thinking provides the full intelligence benefits of extended thinking, while preventing misuse. This is the default behavior on Claude 4 models when the `display` field on the thinking configuration is unset or set to `"summarized"`. On Claude Fable 5, Claude Mythos 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, and Claude Mythos Preview, `display` defaults to `"omitted"` instead, so you must set `display: "summarized"` explicitly to receive summarized thinking.

Here are some important considerations for summarized thinking:

In rare cases where you need access to full thinking output for Claude 4 models, contact Anthropic sales.

The `display` field on the thinking configuration controls how thinking content is returned in API responses. It accepts two values:

`"summarized"`: Thinking blocks contain summarized thinking text. See Summarized thinking for details. This is the default on Claude Opus 4.6, Claude Sonnet 4.6, and earlier Claude 4 models.`"omitted"`: Thinking blocks are returned with an empty `thinking` field. The `signature` field still carries the encrypted full thinking for multi-turn continuity (see Thinking encryption). This is the default on Claude Fable 5, Claude Mythos 5, Claude Sonnet 5, Claude Opus 4.8, Claude Opus 4.7, and Claude Mythos Preview.Setting `display: "omitted"` is useful when your application doesn't surface thinking content to users. The primary benefit is **faster time-to-first-text-token when streaming:** The server skips streaming thinking tokens entirely and delivers only the signature, so the final text response begins streaming sooner.

Here are some important considerations for omitted thinking:

`signature` to reconstruct the original thinking for prompt construction (see Preserving thinking blocks). Any text you place in the `thinking` field of a round-tripped omitted block is ignored.`display` is invalid with `thinking.type: "disabled"` (there is nothing to display).`thinking.type: "adaptive"` and the model skips thinking for a simple request, no thinking block is produced regardless of `display`.The `signature` field is identical whether `display` is `"summarized"` or `"omitted"`. Switching `display` values between turns in a conversation is supported.

The `display` setting controls visibility only. Under every setting, thinking happens and is billed the same.

The default for `thinking.display` depends on the model:

`"omitted"`. Thinking blocks still appear in the response stream, but their `thinking` field is empty unless you explicitly opt in. This is a silent change from Claude Opus 4.6, where the default was `"summarized"`.`"summarized"`. The readable summary appears without opting in.To receive summarized thinking text on models where the default is `"omitted"`, set `thinking.display` to `"summarized"` explicitly:

```
thinking = {
    "type": "adaptive",
    "display": "summarized",
}
```
For code examples and streaming behavior with `display: "omitted"`, see Controlling thinking display on the extended thinking page. The examples there use `type: "enabled"`; with adaptive thinking, use:

`thinking = {"type": "adaptive", "display": "omitted"}`Full thinking content is encrypted and returned in the `signature` field. This field is used to verify that thinking blocks were generated by Claude when passed back to the API.

It is only strictly necessary to send back thinking blocks when using tools with extended thinking. Otherwise you can omit thinking blocks from previous turns. If you pass them back, whether the API keeps or strips them depends on the model: Opus 4.5+ and Sonnet 4.6+ keep them in context by default; earlier Opus/Sonnet models and all Haiku models strip them. See context editing to configure this.

If sending back thinking blocks, pass everything back as you received it for consistency and to avoid potential issues.

Here are some important considerations on thinking encryption:

`signature_delta` inside a `content_block_delta` event just before the `content_block_stop` event.`signature` values are significantly longer in Claude 4 models than in previous models.`signature` field is an opaque field and should not be interpreted or parsed.`signature` values are compatible across platforms (Claude APIs, Amazon Bedrock, and Google Cloud). Values generated on one platform will be compatible with another.On Claude Fable 5 and Claude Mythos 5, the raw chain of thought is never returned. The thinking blocks you receive are regular `thinking` blocks, not `redacted_thinking`. The `thinking.display` setting works the same as on other models:

`"summarized"` returns a readable summary of the reasoning.`"omitted"` (the default on these models) still includes `thinking` blocks in responses, but their `thinking` field is an empty string.For the response shape of thinking blocks, see the Messages API reference.

When continuing a conversation on the same model, pass each thinking block back to the API exactly as received, including blocks whose `thinking` field is empty. Don't edit or reconstruct them. Reading the summary text for display is fine: the API rejects blocks whose content has been modified, not blocks you have read.

When you switch models, for example after a classifier refusal fallback, strip `thinking` and `redacted_thinking` blocks from prior assistant turns. Thinking blocks are tied to the model that produced them. Other models silently ignore them rather than rejecting the request, but ignored blocks still add input tokens.

Two exceptions, covered in Fallback credit:

`fallback` blocks from a mid-output fallback stay where they appeared.To get visibility into the model's reasoning, read the `thinking` blocks described in this section rather than prompting for reasoning in the response text. On Claude Fable 5, a request that attempts to elicit the model's internal reasoning as part of the response text can be refused with `stop_details.category: "reasoning_extraction"`. See Refusal categories for the field reference and handling guidance.

For complete pricing information including base rates, cache writes, cache hits, and output tokens, see the pricing page.

The thinking process incurs charges for:

When extended thinking is enabled, a specialized system prompt is automatically included to support this feature.

When using summarized thinking:

When using `display: "omitted"`:

`thinking` field is empty)The billed output token count will **not** match the visible token count in the response. You are billed for the full thinking process, not the thinking content visible in the response.

To see how many billed output tokens were spent on internal reasoning, read `usage.output_tokens_details.thinking_tokens` in the response. This value reflects the raw reasoning the model generated (not the summarized text returned in the body) and is always less than or equal to `output_tokens`. Subtract it from `output_tokens` to approximate the non-reasoning portion of the output.

```
{
  "usage": {
    "input_tokens": 25,
    "output_tokens": 348,
    "output_tokens_details": {
      "thinking_tokens": 312
    }
  }
}
```
`output_tokens` remains the inclusive, authoritative total used for billing. `output_tokens_details` is a read-only breakdown for observability.

The extended thinking page covers several topics in more detail with mode-specific code examples:

`tool_choice` limitations when thinking is active.`max_tokens` and context window limits.Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency.

Give Claude enhanced reasoning for complex tasks and control how thinking content is returned.

Behavioral differences and prompting patterns for Claude Sonnet 5, covering effort, adaptive thinking defaults, tool use, and migration from Claude Sonnet 4.6.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
