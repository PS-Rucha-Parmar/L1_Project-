---
title: "Fallback credit - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/fallback-credit"
library: "platform"
created: "2026-07-13T07:57:40.049850+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Prompt caches are per-model. When Claude Fable 5 declines a request and you retry on another model, the conversation prefix that was already cached for Claude Fable 5 must be written into the new model's cache from scratch. Cache writes cost more than cache reads. Fallback credit removes that extra cost. The refusal carries a credit token, you echo the token on the retry, and the retry is billed as though the conversation had been on the new model all along.

You need this page only when you build the retry yourself: over raw HTTP or with custom retry logic. Server-side fallback and the SDK middleware apply fallback credit automatically. If you use either, skip this page.

Refusals and fallback covers detecting refusals and choosing a fallback approach. Prompt caching explains cache reads and cache writes if those terms are new.

Opt in with the beta header

Send the request that may be refused with the `anthropic-beta: fallback-credit-2026-06-01` header. The `server-side-fallback-2026-06-01` header also grants the same fields.

Read two fields from the refusal

On a refusal, `stop_details` includes two fields:

`fallback_credit_token`:`fallback_has_prefill_claim`:Both are `null` when no credit is available for the refusal.

Build the retry

Start from the refused request body. Set `model` to the fallback model and add the token as the top-level `fallback_credit_token` parameter. Pick the body shape from the table below.

Send the retry with the same header

Send the retry with the same `fallback-credit-2026-06-01` beta header. The retry needs the header to redeem the token.

The `fallback_has_prefill_claim` field tells you whether the retry can continue the refused model's partial output instead of starting over:

| `fallback_has_prefill_claim` | Retry body | 
|---|---|
| `true` | The refused request body, unchanged, plus one appended assistant message whose `content`echoes the refused response's`content`. The retry model continues the response from where the refused model stopped, and completed server tool calls are not re-executed. | 
| `false` | The refused request body, unchanged. | 

The following example makes a request that may be refused and redeems the credit token on a retry against Claude Opus 4.8. When a retry attempt is rejected, the example degrades through the rejection ladder: the sequence of progressively simpler retry shapes covered in When a retry is rejected.

```
client = Anthropic()
request = {
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude"}],
}
def send(model: str, body: dict[str, object]) -> BetaMessage:
    return client.beta.messages.create(
        model=model, betas=["fallback-credit-2026-06-01"], **body
    )
response = send("claude-fable-5", request)
if (
    response.stop_reason == "refusal"
    and (details := response.stop_details)
    and (token := details.fallback_credit_token)
):
    exact_body = request | {"fallback_credit_token": token}
    # Prefer the continuation shape unless the claim is False
    if details.fallback_has_prefill_claim is not False:
        echoed = [block.model_dump() for block in response.content]
        match echoed:
            case [*_, {"type": "text"} as final_block]:
                final_block["text"] = final_block["text"].rstrip()
        attempt = exact_body | {
            "messages": [
                *request["messages"],
                {"role": "assistant", "content": echoed},
            ]
        }
    else:
        attempt = exact_body
    try:
        response = send("claude-opus-4-8", attempt)
    except BadRequestError as error:
        if "redemption temporarily unavailable" in error.message:
            raise  # Transient: retry with the token within its five-minute window
        try:
            # Fall back to the unchanged body, still with the token
            response = send("claude-opus-4-8", exact_body)
        except BadRequestError as retry_error:
            if "redemption temporarily unavailable" in retry_error.message:
                raise  # Transient: retry with the token within its five-minute window
            # The token itself was rejected: forfeit it and retry without.
            response = send("claude-opus-4-8", request)
print(json.dumps({"stop_reason": response.stop_reason, "model": response.model}))
```
Fallback credit is in beta on the Claude API, Claude Platform on AWS, Amazon Bedrock, Google Cloud, and Microsoft Foundry. Credit tokens returned in Message Batches results cannot be redeemed. Redemption applies only to direct Messages API requests.

The retry model must be one of the refused model's permitted fallback targets. At launch, Claude Fable 5's permitted target is Claude Opus 4.8 (`claude-opus-4-8`).

The refund is visible in the retry's `usage`. Compared with what the same request would report without the token, `cache_creation_input_tokens` is lower, and `cache_read_input_tokens` is higher by the same amount. A shift of zero means the token was honored but there was nothing to reprice, for example because the retry model's cache was already warm.

Most retries redeem on the first attempt. When one does not, the API returns a 400 error that tells you what to try next.

Continuation rejected: resend the unchanged body

If the retry that appends the assistant message is rejected with a 400 error, resend the refused request body unchanged, still with the token.

Token rejected: drop the token

If the unchanged body is also rejected with a 400 error whose message names `fallback_credit_token`, retry without the token. The credit is forfeited, but the retry itself goes through.

If the refused request executed server tools, a tokenless retry re-runs and re-bills those tools. In that case, surface the 400 error to your caller instead of falling through to a tokenless retry.

The sections below cover edge cases and the complete redemption rules. Most integrations do not need them.

Detect refusals and choose between server-side fallback, the SDK middleware, and a manual retry.

How cache reads and cache writes are billed.

Every `stop_reason` value and how to handle it.

The SDK helper that applies fallback credit automatically.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/fallback-credit](https://platform.claude.com/docs/en/build-with-claude/fallback-credit)
