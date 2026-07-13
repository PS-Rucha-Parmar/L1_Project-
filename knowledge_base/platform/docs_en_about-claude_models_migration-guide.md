---
title: "Migration guide - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/about-claude/models/migration-guide"
library: "platform"
created: "2026-07-13T07:52:57.385807+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This guide covers migrating Messages API code. If you use Claude Managed Agents, no changes beyond updating the model name are required.

**Automate your migration with the Claude API skill.** In Claude Code, run `/claude-api migrate` to invoke the bundled Claude API skill. It works for any target model on this page:

`/claude-api migrate this project to claude-opus-4-8`The skill applies the model ID swap and, as needed, breaking parameter changes, prefill replacement, and effort calibration for your target model across your code base, then produces a checklist of items to verify manually. It asks you to confirm the migration scope (entire working directory, a subdirectory, or a specific file list) before editing any files. The skill also detects Amazon Bedrock, Google Cloud, Claude Platform on AWS, and Microsoft Foundry clients and adjusts model ID formats and feature changes for each platform.

Claude Mythos 5 is the access-gated model offered in limited availability to approved customers in Project Glasswing. It shares the same specs and pricing as Claude Fable 5: a 1M token context window by default, and up to 128k output tokens per request.

The baseline settings for `claude-mythos-5`:

`thinking` configuration is required. Both `thinking: {type: "disabled"}` and manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) return a 400 error.Claude Mythos 5 is the access-gated successor to Claude Mythos Preview, the invitation-only research preview. For a generally available model with the same capabilities, see Claude Fable 5.

Migration is mostly drop-in. Claude Mythos 5 uses the same Messages API and the same tool use patterns as Claude Mythos Preview, and token counts are roughly unchanged because both models use the same tokenizer. The key changes to check are the features that are no longer available (listed in the next section) and thinking output.

For the Claude Mythos Preview retirement timeline, see Model deprecations.

```
model = "claude-mythos-preview"  # Before
model = "claude-mythos-5"  # After
```
**Extended thinking and thinking token budgets:** Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is not supported on `claude-mythos-5` and returns a 400 error. Adaptive thinking is always on: the model determines when and how much to think on each request, and no `thinking` configuration is required. `thinking: {type: "disabled"}` returns an error. `budget_tokens` has no direct replacement: thinking is adaptive, and the effort parameter is a separate output-level control, not a thinking budget.

Before (Claude Mythos Preview):

```
client.messages.create(
    model="claude-mythos-preview",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "..."}],
)
```
After (Claude Mythos 5):

```
client.messages.create(
    model="claude-mythos-5",
    max_tokens=16000,
    messages=[{"role": "user", "content": "..."}],
)
```
**Assistant prefill:** Prefilling the assistant message is not supported on `claude-mythos-5` and returns a 400 error, the same as on Claude Mythos Preview. Use system prompt instructions instead.

**Thinking output:** On `claude-mythos-5`, the raw chain of thought is never returned, but thinking blocks still carry readable summarized text when `thinking.display` is set to `summarized`. Pass thinking blocks back unchanged when continuing a conversation on the same model. See Thinking output on Claude Fable 5 and Claude Mythos 5.

`claude-mythos-5` uses the same tokenizer as `claude-mythos-preview` (the tokenizer introduced with Claude Opus 4.7). Token counts are roughly unchanged when migrating from `claude-mythos-preview`. Compared with models before Claude Opus 4.7, the same content can tokenize to roughly 30% more tokens, varying by content and workload shape.

`/v1/messages/count_tokens` returns roughly unchanged values for `claude-mythos-5` compared with `claude-mythos-preview`. Re-baseline cost and latency on your own workloads.

`claude-mythos-preview` to `claude-mythos-5`.`thinking: {type: "enabled", budget_tokens: N}`). Adaptive thinking is always on, and no `thinking` field is required.`thinking: {type: "disabled"}` configuration. Disabling thinking returns an error on `claude-mythos-5`.`budget_tokens`. It has no direct replacement: thinking is adaptive, and the `effort` parameter is a separate output-level control, not a thinking budget.`thinking` field treats it as display text only and passes thinking blocks back unchanged when continuing on the same model. `thinking.display` defaults to `"omitted"` on `claude-mythos-5`, the same as on Claude Mythos Preview; set `display: "summarized"` to receive readable summaries. See Thinking output on Claude Fable 5 and Claude Mythos 5.`thinking` and `redacted_thinking` blocks from prior assistant turns first. Thinking blocks from `claude-mythos-5` are tied to the model that produced them, and models other than Claude Fable 5 and Claude Mythos 5 silently ignore them. Stripping keeps cross-model requests minimal and uniform.`claude-mythos-preview`.Claude Fable 5 is Anthropic's most capable widely released model, generally available on the Claude API, Claude Platform on AWS, Amazon Bedrock, Google Cloud, and Microsoft Foundry.

Migration is mostly drop-in. Claude Fable 5 uses the same Messages API and the same tool use patterns as Claude Opus 4.8. It supports the same 1M token context window by default and the same 128k max output tokens. Token counts are roughly unchanged because both models use the same tokenizer.

The key changes to check are always-on adaptive thinking, thinking output, safety classifier refusals, and pricing. Before you migrate covers pricing and data retention; What changed covers the rest.

Claude Fable 5 is priced at $10 per million input tokens and $50 per million output tokens, compared with $5 and $25 for Claude Opus 4.8. See Claude pricing for details.

Claude Fable 5 requires 30-day data retention and is not available under zero data retention (ZDR) arrangements; it is designated a Covered Model. On the Claude API, a request from an organization whose data retention configuration does not meet this requirement returns a 400 `invalid_request_error`. Organizations with a ZDR arrangement should contact their Anthropic account team to discuss data retention configuration; Claude Opus 4.8 remains available under ZDR. Alternatively, you can configure data retention per workspace. The 30-day data retention requirement applies on every platform where Claude Fable 5 is offered; see Model-specific data retention requirements for per-platform details.

If your code is on Claude Opus 4.7 or earlier, first apply the relevant Migrating to Claude Opus 4.8 sub-section for your current model. Those sections cover breaking changes (sampling parameters rejected, manual extended thinking rejected, prefill removed, new tokenizer) that this section does not repeat.

```
model = "claude-opus-4-8"  # Before
model = "claude-fable-5"  # After
```
The items in this section describe the API and behavior differences worth checking after you swap the model ID.

**Adaptive thinking is always on:** Adaptive thinking is the only thinking mode on `claude-fable-5`. The model determines when and how much to think on each request, and no `thinking` configuration is required. `thinking: {type: "disabled"}` returns an error. Use the effort parameter to control thinking depth.

The behavior change to check: on Claude Opus 4.8, requests without a `thinking` field run without thinking; on `claude-fable-5`, those same requests run with adaptive thinking. `max_tokens` remains a hard limit on total output, thinking plus response text, so revisit it for workloads that ran without thinking on Claude Opus 4.8. See Cost control.

Before (Claude Opus 4.8):

```
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "..."}],
)
```
After (Claude Fable 5):

```
client.messages.create(
    model="claude-fable-5",
    max_tokens=16000,
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "..."}],
)
```
**Extended thinking and thinking budgets (unchanged):** Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is not supported on `claude-fable-5` and returns a 400 error, the same as on Claude Opus 4.8. `budget_tokens` has no direct replacement: thinking is adaptive, and the effort parameter is a separate output-level control, not a thinking budget.

**Assistant prefill (unchanged):** Prefilling the assistant message is not supported on `claude-fable-5` and returns a 400 error, the same as on Claude Opus 4.8. Use system prompt instructions instead.

**Thinking output:** On `claude-fable-5`, the raw chain of thought is never returned, but thinking blocks still carry readable summarized text when `thinking.display` is set to `summarized`. Pass thinking blocks back unchanged when continuing a conversation on the same model. See Thinking output on Claude Fable 5 and Claude Mythos 5.

**Safety classifiers and the  refusal stop reason:** 

`claude-fable-5` runs safety classifiers on requests and during response generation. When a classifier declines a request, the Messages API returns `stop_reason: "refusal"` as a successful HTTP 200 response, not an error. The `stop_details.category` field reports which classifier fired, with categories such as `"cyber"`, `"bio"`, and `"reasoning_extraction"`, or `null` when the refusal maps to no named category. See the refusal category table for the full set.You are not billed for the input tokens of a request refused before any output is generated. When a classifier fires mid-stream, the input and already-streamed output are billed; discard the partial output.

To re-run refused requests on another model automatically, pass the opt-in `fallbacks` parameter, which is in beta on the Claude API and Claude Platform on AWS. The parameter is not available on the Message Batches API or on Amazon Bedrock, Google Cloud, and Microsoft Foundry; on those three platforms, run the retry client-side or use the SDK refusal-fallback middleware. See Handling stop reasons.

**Start at  high effort:** The effort parameter default remains 

`high`. On Claude Opus 4.8, the recommendation for coding and high-autonomy work is to set `xhigh` explicitly. On `claude-fable-5`, use `high` as the default for most tasks and reserve `xhigh` for the most capability-sensitive workloads. Lower effort settings on `claude-fable-5` still perform well and often exceed `xhigh` performance on prior models. Reduce effort if a task completes but takes longer than necessary. See Prompting Claude Fable 5.**Lower prompt caching minimum:** The minimum cacheable prompt length on `claude-fable-5` is 512 tokens, lower than the 1,024 tokens on Claude Opus 4.8. Prompts that were too short to cache on Claude Opus 4.8 can now create cache entries, with no code changes required. On Amazon Bedrock, the minimum for `claude-fable-5` is 1,024 tokens. See Prompt caching for per-model minimums.

`claude-fable-5` requires 30-day data retention and, on the Claude API, returns a 400 `invalid_request_error` otherwise. See Model-specific data retention requirements.`claude-opus-4-8` to `claude-fable-5`.`thinking: {type: "disabled"}` configuration. Disabling thinking returns an error on `claude-fable-5`, and requests without a `thinking` field run with adaptive thinking.`claude-fable-5`.`thinking` field treats it as display text only and passes thinking blocks back unchanged when continuing on the same model. `thinking.display` defaults to `"omitted"` on `claude-fable-5`, the same as on Claude Opus 4.8; set `display: "summarized"` to receive readable summaries. See Thinking output on Claude Fable 5 and Claude Mythos 5.`thinking` and `redacted_thinking` blocks from prior assistant turns first. Thinking blocks from `claude-fable-5` are tied to the model that produced them, and models other than Claude Fable 5 and Claude Mythos 5 silently ignore them. Stripping keeps cross-model requests minimal and uniform. The exception is redeeming a fallback credit, which requires the request body echoed under that feature's exact rules.`stop_reason: "refusal"` and read the `stop_details.category` field. To re-run refused requests on another model automatically, consider the opt-in `fallbacks` parameter (beta). See Handling stop reasons.`effort` setting. Start at `high` for most tasks, including workloads that ran at `xhigh` on Claude Opus 4.8.`claude-opus-4-8`; per-token pricing differs.Claude Opus 4.8 is built for complex agentic coding and enterprise work. These are the baseline settings for `claude-opus-4-8`. The following sub-sections cover the specific changes to make from each earlier Opus model.

`thinking: {type: "adaptive"}`) is the supported thinking mode and is off by default: requests with no `thinking` field run without thinking. Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) returns a 400 error.`high` across all surfaces. For coding and high-autonomy work, set `xhigh` explicitly.`temperature`, `top_p`, and `top_k` set to a non-default value return a 400 error. Omit them and use prompting to guide the model's behavior.`output_config.format` instead.Claude Opus 4.8 also supports prompt caching, batch processing, the Files API, PDF support, vision, the full set of server-side and client-side tools, mid-conversation system messages, and refusal stop details.

Claude Opus 4.8 builds on Claude Opus 4.7.

Claude Opus 4.8 should have strong out-of-the-box performance on existing Claude Opus 4.7 prompts and evals. There are no breaking API changes for code already running on Claude Opus 4.7. It supports the same set of features as Claude Opus 4.7, including the 1M token context window, 128k max output tokens, adaptive thinking, prompt caching, batch processing, the Files API, PDF support, vision, and the full set of server-side and client-side tools. It also adds mid-conversation system messages and publicly documents refusal stop details.

If your code is on Claude Opus 4.6 or earlier, use Migrating to Claude Opus 4.8 from Claude Opus 4.6 or Migrating to Claude Opus 4.8 from Claude Opus 4.5 or earlier instead. Those sections include breaking changes (sampling parameters rejected, manual extended thinking rejected, new tokenizer) that the upgrade from Claude Opus 4.7 alone does not cover.

```
# Opus migration
model = "claude-opus-4-7"  # Before
model = "claude-opus-4-8"  # After
```
These are not breaking changes. Code that runs on Claude Opus 4.7 continues to work unchanged on Claude Opus 4.8. The items below describe behavior differences worth checking after you swap the model ID.

**Sampling parameters (unchanged):** Setting `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Claude Opus 4.8, the same as on Claude Opus 4.7. The SDK request types still define these fields for compatibility with earlier models, so code that sets them type-checks, but the API rejects the request server-side. If you removed these parameters when migrating to Opus 4.7, no further changes are needed.

**Effort default is  high:** The effort parameter default on Claude Opus 4.8 is 

`high` across all surfaces, including Claude Code and the Messages API. If you already set effort explicitly, your setting is unchanged. For coding and high-autonomy work, set `xhigh` explicitly. Re-evaluate your effort setting against your latency and cost budget.**1M context window is the default:** Claude Opus 4.8 serves the full 1M token context window by default with no beta header and no long-context premium. If your client passes a context-window beta header for compatibility with older models, you can remove it on Claude Opus 4.8.

**Mid-conversation system messages:** Claude Opus 4.8 accepts `role: "system"` messages immediately after a user turn in the `messages` array (subject to placement rules). Use the top-level `system` field for instructions that apply from the start. Earlier models, including Claude Opus 4.7, reject `role: "system"` in `messages` with a 400 error. If you maintain code paths that rebuild the full message history to update instructions, you can simplify them and preserve prompt cache hits on earlier turns.

**Refusal stop details:** The `stop_details` object on refusal responses (available since Claude Opus 4.7) is now publicly documented. When the model declines a request, it identifies the category of refusal, in addition to the existing `refusal` stop reason. No beta header is required, and there is no opt-out. See Handling stop reasons.

**Lower prompt caching minimum:** The minimum cacheable prompt length on Claude Opus 4.8 is 1,024 tokens, lower than on Claude Opus 4.7. Prompts that were too short to cache on Claude Opus 4.7 can now create cache entries, with no code changes required. See Prompt caching for per-model minimums.

**Effort levels recalibrated:** The token allocation behind each effort level changes on Claude Opus 4.8 compared to Claude Opus 4.7: `medium` allows somewhat more thinking, `high` somewhat less, and `xhigh` substantially more. If you tuned an effort level against Claude Opus 4.7 cost or latency, re-baseline at the same level before adjusting it. See Effort.

`claude-opus-4-7` to `claude-opus-4-8` (or update aliases).`effort` setting. The default is `high` across all surfaces; for coding and high-autonomy work, set `xhigh` explicitly.`stop_details` on refusals (available since Claude Opus 4.7; now publicly documented).Claude Opus 4.8 should have strong out-of-the-box performance on existing Claude Opus 4.6 prompts and evals at the same pricing, but there are a handful of behavioral and API changes worth knowing about as you migrate. These changes took effect in Claude Opus 4.7, and there are no additional breaking API changes between Claude Opus 4.7 and Claude Opus 4.8. It supports the same set of features as Claude Opus 4.6, including:

```
# Opus migration
model = "claude-opus-4-6"  # Before
model = "claude-opus-4-8"  # After
```
**Extended thinking removed:** `thinking: {type: "enabled", budget_tokens: N}` is no longer supported on Claude Opus 4.7 or later models and returns a 400 error. Switch to adaptive thinking (`thinking: {type: "adaptive"}`) and use the effort parameter to control thinking depth. Adaptive thinking is **off by default** on Claude Opus 4.7: requests with no `thinking` field run without thinking, matching Opus 4.6 behavior. Set `thinking: {type: "adaptive"}` explicitly to enable it.

Before (Claude Opus 4.6):

```
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "..."}],
)
```
After (Claude Opus 4.8):

```
client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # or "max", "xhigh", "medium", "low"
    messages=[{"role": "user", "content": "..."}],
)
```
Adaptive thinking is steerable through prompting. For guidance on tuning when the model over- or under-thinks, see Calibrating effort and thinking depth.

**Sampling parameters removed:** Setting `temperature`, `top_p`, or `top_k` to any non-default value on Claude Opus 4.7 returns a 400 error. The safest migration path is to omit these parameters entirely from request payloads. Prompting is the recommended way to guide model behavior on Claude Opus 4.7. If you were using `temperature = 0` for determinism, note that it never guaranteed identical outputs on prior models.

**Thinking content omitted by default:** Thinking blocks still appear in the response stream on Claude Opus 4.7, but their `thinking` field is empty unless you explicitly opt in. This is a silent change from Claude Opus 4.6, where the default was to return summarized thinking text. To restore summarized thinking content on Claude Opus 4.7, set `thinking.display` to `"summarized"`:

```
thinking = {
    "type": "adaptive",
    "display": "summarized",
}
```
The default is `"omitted"` on Claude Opus 4.7. If your product streams reasoning to users, the new default appears as a long pause before output begins; set `display: "summarized"` to restore visible progress during thinking. See Extended thinking for details.

**Updated token counting:** Claude Opus 4.7 uses a new tokenizer, contributing to its improved performance on a wide range of tasks. The new tokenizer may use roughly 1x to 1.35x as many tokens when processing text compared to previous models (up to ~35% more, varying by content).

`/v1/messages/count_tokens` will return a different number of tokens for Claude Opus 4.7 than it did for Claude Opus 4.6. Token efficiency can vary by workload shape.

Prompting interventions, `task_budget`, and `effort` can help control costs and ensure appropriate token usage. These controls may trade off model intelligence. Update your `max_tokens` parameters to give additional headroom, including compaction triggers. Claude Opus 4.7 provides a 1M context window at standard API pricing with no long-context premium.

**Prefill removal (carried over from Opus 4.6):** Prefilling assistant messages returns a 400 error on Claude Opus 4.7. Use structured outputs, system prompt instructions, or `output_config.format` instead.

The effort parameter allows you to tune Claude's intelligence vs. token spend, trading off capability for faster speed and lower costs. Start with the `xhigh` effort level for coding and agentic use cases, and use a minimum of `high` effort for most intelligence-sensitive use cases. Experiment with other effort levels to further tune token usage and intelligence:

`max`:`xhigh`:`high`:`high` effort.`medium`:`low`:Effort is more important for this model than for any prior Opus. Experiment with it actively when you upgrade.

Claude Opus 4.7 has several behavioral differences from Claude Opus 4.6 that are not API breaking changes but may require prompt updates or scaffolding removal.

**Response length varies by use case:** Claude Opus 4.7 calibrates response length to how complex it judges the task to be, rather than defaulting to a fixed verbosity. This usually means shorter answers on simple lookups and much longer ones on open-ended analysis.

If your product depends on a certain style or verbosity of output, you may need to tune your prompts. For example, to decrease verbosity, add: "Provide concise, focused responses. Skip non-essential context, and keep examples minimal." If you see specific kinds of over-explaining, add targeted instructions in your prompt to prevent them.

Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do.

**More literal instruction following:** Claude Opus 4.7 interprets prompts more literally and explicitly than Claude Opus 4.6, particularly at lower effort levels. It will not silently generalize an instruction from one item to another, and it will not infer requests you didn't make. The upside of this literalism is precision and less thrash. It generally performs better for API use cases with carefully tuned prompts, structured extraction, and pipelines where you want predictable behavior. A prompt and harness review may be especially helpful for migration to Claude Opus 4.8.

**More direct tone:** As with any new model, prose style on long-form writing may shift. Claude Opus 4.7 is more direct and opinionated, with less validation-forward phrasing and fewer emoji than Claude Opus 4.6's warmer style. If your product relies on a specific voice, re-evaluate style prompts against the new baseline.

**Built-in progress updates in agentic traces:** Claude Opus 4.7 provides more regular, higher-quality updates to the user throughout long agentic traces. If you've added scaffolding to force interim status messages ("After every 3 tool calls, summarize progress"), try removing it. If you find that the length or contents of Claude Opus 4.7's user-facing updates are not well-calibrated to your use case, explicitly describe what these updates should look like in the prompt and provide examples.

**Fewer subagents spawned by default:** Claude Opus 4.7 tends to spawn fewer subagents by default. However, this behavior is steerable through prompting; give Claude Opus 4.7 explicit guidance around when subagents are desirable.

**Stricter effort calibration:** Meaningfully changing from Claude Opus 4.6, Claude Opus 4.7 respects effort levels strictly, especially at the low end. At `low` and `medium`, the model scopes its work to what was asked rather than going above and beyond.

This is good for latency and cost, but on moderately complex tasks running at `low` effort there is some risk of under-thinking. If you observe shallow reasoning on complex problems, raise effort to `high` or `xhigh` rather than prompting around it.

If you need to keep effort at `low` for latency, add targeted guidance: "This task involves multi-step reasoning. Think carefully through the problem before responding." See Recommended effort levels for Claude Opus 4.7.

**Fewer tool calls by default:** Claude Opus 4.7 has a tendency to use tools less often than Claude Opus 4.6 and to use reasoning more. This produces better results in most cases.

To increase tool usage, raise the effort setting. `high` or `xhigh` effort settings show substantially more tool usage in agentic search and coding. You can also adjust your prompt to explicitly instruct the model about when and how to properly use its tools.

**Real-time cybersecurity safeguards:** Newly added in Claude Opus 4.7, requests that involve prohibited or high-risk topics may lead to refusals. For legitimate security work such as penetration testing, vulnerability research, or red-teaming, apply to the Cyber Verification Program to request reduced restrictions. See Safeguards, warnings, and appeals for background.

**High-resolution image support:** Claude Opus 4.7 is the first Claude model with high-resolution image support. Maximum image resolution is 2576 pixels on the long edge, up from 1568 pixels on prior models. This unlocks gains on vision-heavy workloads and is particularly valuable for computer use, screenshot understanding, and document analysis.

High-resolution support is automatic and requires no beta header or client-side opt-in. Two things to plan for:

`max_tokens` and cost expectations for image-heavy workloads, or downsample before sending if you do not need the additional fidelity.See High-resolution image support on Claude Opus 4.7 for details.

These are not required but will improve your experience:

**Re-evaluate  max_tokens:** Because the same text produces a higher token count on Claude Opus 4.7 and later models, update your 

`max_tokens` parameters to give additional headroom, including compaction triggers. Prompting interventions, `task_budget`, and `effort` can help control costs and ensure appropriate token usage.**Audit token-count expectations:** Any code path that estimates tokens client-side or assumes a fixed token-to-character ratio should be re-tested against Claude Opus 4.8. Use the Token counting endpoint to verify.

**Adopt task budgets (beta):** Claude Opus 4.7 introduces task budgets. These budgets let you inform Claude how many tokens it has for a full agentic loop, including thinking, tool calls, tool results, and final output. The model sees a running countdown and uses it to prioritize work and finish the task gracefully as the budget is consumed. To use, set the beta header `task-budgets-2026-03-13` and add the following to your output config:

```
output_config = {
    "effort": "high",
    "task_budget": {"type": "tokens", "total": 128000},
}
```
You may need to experiment with different task budgets for your use case. If the model is given a task budget that is too restrictive, it may complete the task less thoroughly, referencing its budget as the constraint.

For open-ended agentic tasks where quality matters more than speed, do not set a task budget. Reserve task budgets for workloads where you need the model to scope its work to a token allowance. The minimum value for a task budget is 20k tokens.

A task budget is not a hard cap; it's a suggestion that the model is aware of. It differs from `max_tokens`:

`task_budget`:`max_tokens`:Use `task_budget` when you want the model to self-moderate, and `max_tokens` as a hard ceiling to cap usage.

**Set a large  max_tokens at max or xhigh effort:** If you are running Claude Opus 4.7 or a later model at 

`max` or `xhigh` effort, set a large max output token budget so the model has room to think and act across its subagents and tool calls. Start at 64k tokens and tune from there.**Downsample images if high resolution is unnecessary:** Claude Opus 4.7 supports images up to 2576px / 3.75MP. High-res images use more tokens. If the additional image fidelity is unnecessary, downsample images before sending to Claude to avoid token-usage increases. See Images and vision.

`claude-opus-4-6` to `claude-opus-4-8` (or update aliases).`temperature`, `top_p`, and `top_k` from request payloads.`thinking: {type: "enabled", budget_tokens: N}` with `thinking: {type: "adaptive"}` plus the effort parameter.`max_tokens` to account for the updated tokenization.`xhigh` or `max` effort, raise `max_tokens` to at least 64k as a starting point.If you are migrating from Claude Opus 4.5, Opus 4.1 (deprecated), or an earlier model directly to Claude Opus 4.8, apply **all of the changes in Migrating to Claude Opus 4.8 from Claude Opus 4.6** plus the cumulative changes in this section that took effect between Opus 4.5 and Opus 4.7. If you are migrating from Opus 4.6, you only need the from Claude Opus 4.6 section.

```
# Opus migration
model = "claude-opus-4-5"  # Before
model = "claude-opus-4-8"  # After
```
**Prefill removal** is covered in the breaking changes for migrating from Claude Opus 4.6.

**Tool parameter quoting:** Claude Opus 4.6 and later models may produce slightly different JSON string escaping in tool call arguments (for example, different handling of Unicode escapes or forward slash escaping). If you parse tool call `input` as a raw string rather than using a JSON parser, verify your parsing logic. Standard JSON parsers (like `json.loads()` or `JSON.parse()`) handle these differences automatically.

These changes improve your experience on Claude Opus 4.7 and later models. Items marked **(required on Opus 4.7)** were optional recommendations when Opus 4.6 launched but are now mandatory; the rest remain recommended.

**Migrate to adaptive thinking (required on Opus 4.7):** `thinking: {type: "enabled", budget_tokens: N}` returns a 400 error on Claude Opus 4.7. Switch to `thinking: {type: "adaptive"}` and use the effort parameter to control thinking depth. See Adaptive thinking.

```
response = client.beta.messages.create(
    model="claude-opus-4-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 32000},
    betas=["interleaved-thinking-2025-05-14"],
    messages=[{"role": "user", "content": "Your prompt here"}],
)
```
Note that the migration also moves from `client.beta.messages.create` to `client.messages.create`. Adaptive thinking and effort are GA features and do not require the beta SDK namespace or any beta headers.

**Remove effort beta header:** The effort parameter is now GA. Remove `betas=["effort-2025-11-24"]` from your requests.

**Remove fine-grained tool streaming beta header:** Fine-grained tool streaming is now GA. Remove `betas=["fine-grained-tool-streaming-2025-05-14"]` from your requests.

**Remove interleaved thinking beta header:** Adaptive thinking automatically enables interleaved thinking on Claude Opus 4.7, Opus 4.6, and Sonnet 4.6. Remove `betas=["interleaved-thinking-2025-05-14"]` from your requests. The header is still functional on Sonnet 4.6 with manual extended thinking, but manual mode is deprecated.

**Migrate to output_config.format:** If using structured outputs, update `output_format={...}` to `output_config={"format": {...}}`. The old parameter remains functional but is deprecated and will be removed in a future model release.

If you're migrating from Opus 4.1 (deprecated) or earlier models directly to Claude Opus 4.8, apply the Migrating to Claude Opus 4.8 from Claude Opus 4.6 changes and the cumulative changes earlier in this section, plus the additional changes in this sub-section.

```
# From Opus 4.1
model = "claude-opus-4-1-20250805"  # Before
model = "claude-opus-4-8"  # After
# From Sonnet 3.7
model = "claude-3-7-sonnet-20250219"  # Before
model = "claude-opus-4-8"  # After
```
**Remove sampling parameters**

This is a breaking change when migrating from Claude 3.x models.

Starting with Claude Opus 4.7, setting `temperature`, `top_p`, or `top_k` to any non-default value will return a 400 error. The safest migration path is to omit these parameters entirely from requests, and to use prompting to guide the model's behavior. If you were using `temperature = 0` for determinism, note that it never guaranteed identical outputs.

```
# Before - This will error in Claude 4+ models
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    temperature=0.7,
    top_p=0.9,  # Non-default sampling params return 400 on Opus 4.7
    # ...
)
# After
response = client.messages.create(
    model="claude-opus-4-8",
    # ...
)
```
**Update tool versions**

This is a breaking change when migrating from Claude 3.x models.

Update to the latest tool versions. Remove any code using the `undo_edit` command.

```
# Before
tools = [{"type": "text_editor_20250124", "name": "str_replace_editor"}]
# After
tools = [{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}]
```
`text_editor_20250728` and `str_replace_based_edit_tool`. See Text editor tool documentation for details.`code_execution_20260521`. See Code execution tool documentation for migration instructions.**Handle the  refusal stop reason**

Update your application to handle `refusal` stop reasons:

```
response = client.messages.create(...)
if response.stop_reason == "refusal":
    # Handle refusal appropriately
    pass
```
**Handle the  model_context_window_exceeded stop reason**

Claude 4.5+ models return a `model_context_window_exceeded` stop reason when generation stops because of hitting the context window limit, rather than the requested `max_tokens` limit. Update your application to handle this new stop reason:

```
response = client.messages.create(...)
if response.stop_reason == "model_context_window_exceeded":
    # Handle context window limit appropriately
    pass
```
**Verify tool parameter handling (trailing newlines)**

Claude 4.5+ models preserve trailing newlines in tool call string parameters that were previously stripped. If your tools rely on exact string matching against tool call parameters, verify your logic handles trailing newlines correctly.

**Update your prompts for behavioral changes**

Claude 4+ models have a more concise, direct communication style and require explicit direction. Review prompting best practices for optimization guidance.

`token-efficient-tools-2025-02-19` and `output-128k-2025-02-19`. All Claude 4+ models have built-in token-efficient tool use and these headers have no effect.`claude-opus-4-8``output_config.format` instead`thinking: {type: "enabled", budget_tokens: N}` with `thinking: {type: "adaptive"}` plus the effort parameter (returns 400 on Opus 4.7)`effort-2025-11-24` beta header (effort is now GA)`fine-grained-tool-streaming-2025-05-14` beta header`interleaved-thinking-2025-05-14` beta header (adaptive thinking enables interleaved thinking automatically)`output_format` to `output_config.format` (if applicable)`temperature`, `top_p`, and `top_k` (non-default values return 400 on Opus 4.7)`text_editor_20250728`, `code_execution_20260521`)`refusal` stop reason`model_context_window_exceeded` stop reason`token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`)Claude Sonnet 5 offers the best combination of speed and intelligence in the Claude model family. It builds on Claude Sonnet 4.6.

Claude Sonnet 5 is a drop-in upgrade for Claude Sonnet 4.6. Introductory pricing of $2/$10 per million input/output tokens is in effect through August 31, 2026, after which the standard pricing of $3/$15 per million input/output tokens will take effect; see Pricing for details. There are two breaking API changes for code already running on Claude Sonnet 4.6: manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) and sampling parameters (`temperature`, `top_p`, `top_k`) set to non-default values are no longer accepted and return a 400 error. Use adaptive thinking with the effort parameter instead. Claude Sonnet 5 supports the same set of features as Claude Sonnet 4.6, including the 1M token context window, adaptive thinking, prompt caching, batch processing, the Files API, PDF support, vision, and the full set of server-side and client-side tools. Priority Tier is not available on Claude Sonnet 5. Claude Sonnet 5 also uses a new tokenizer.

If your code is on Claude Sonnet 4.5 or earlier, also apply Migrating to Claude Sonnet 5 from Claude Sonnet 4.5 or earlier. Those steps include breaking changes (assistant message prefilling rejected, tool parameter JSON escaping differences) that this section alone does not cover.

```
# Sonnet migration
model = "claude-sonnet-4-6"  # Before
model = "claude-sonnet-5"  # After
```
Items 4 and 5 in the following list are breaking changes. `max_tokens` remains a hard limit on total output (thinking plus response text), so revisit it for workloads that ran without thinking on Claude Sonnet 4.6.

**New tokenizer:** Claude Sonnet 5 uses a new tokenizer. The same input text produces approximately 30% more tokens than on Claude Sonnet 4.6. The exact increase depends on the content. Requests, responses, and streaming events keep the same shape, and no code changes are required, but anything you measure or budget in tokens shifts: `usage` fields and token counting results for the same text are higher, the 1M token context window holds less text, and a `max_tokens` limit tuned for Claude Sonnet 4.6 may truncate equivalent output. Per-token pricing is unchanged, so the cost of an equivalent request can differ. Re-run token counting against Claude Sonnet 5 rather than reusing counts measured against earlier models.

**128k max output tokens (unchanged):** Claude Sonnet 5 supports up to 128k output tokens, the same as Claude Sonnet 4.6. Existing `max_tokens` values remain valid. Account for the new tokenizer when sizing them.

**Assistant message prefilling (unchanged):** Prefilling the assistant message returns a `400` error on Claude Sonnet 5, the same as on Claude Sonnet 4.6. If you removed prefill when migrating to Claude Sonnet 4.6, no further changes are needed. Use structured outputs, system prompt instructions, or `output_config.format` instead.

**Adaptive thinking on by default:** On Claude Sonnet 4.6, requests without a `thinking` field run without thinking; on Claude Sonnet 5, the same requests run with adaptive thinking. To turn thinking off, pass `thinking: {type: "disabled"}`. Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is not supported and returns a 400 error. Use the effort parameter (default `high`) to control thinking depth.

**Sampling parameters removed:** Sampling parameters (`temperature`, `top_p`, `top_k`) set to a non-default value are not accepted and return a 400 error.

**Cybersecurity safeguards:** Claude Sonnet 5 is the first Sonnet-tier model with real-time cybersecurity safeguards. Requests that involve prohibited or high-risk cybersecurity topics may be refused. Refusals return as a successful HTTP 200 response with `stop_reason: "refusal"`, not an error. See Safeguards, warnings, and appeals for background.

`claude-sonnet-4-6` to `claude-sonnet-5`.`max_tokens` limits sized close to your expected output length, and raise them up to the 128k maximum (unchanged from Claude Sonnet 4.6) where useful.`thinking: {type: "enabled", budget_tokens: N}` configuration (returns a 400 error). Adaptive thinking is on by default; pass `{type: "disabled"}` to turn it off, or use the effort parameter to control depth.`temperature`, `top_p`, and `top_k` parameters set to non-default values (they return a 400 error on Claude Sonnet 5).`stop_reason: "refusal"` if your workload may touch cybersecurity topics.`max_tokens` for workloads that previously ran without thinking.If you are migrating from Claude Sonnet 4.5 or an earlier Sonnet model directly to Claude Sonnet 5, apply the Migrating to Claude Sonnet 5 from Claude Sonnet 4.6 changes plus the changes in this section.

Claude Sonnet 5 defaults to an effort level of `high`, in contrast to Sonnet 4.5 which had no effort parameter. Consider adjusting the effort parameter as you migrate. If not explicitly set, you may experience higher latency with the default effort level.

**Prefilling assistant messages is no longer supported**

This is a breaking change when migrating from Sonnet 4.5 or earlier.

Prefilling assistant messages returns a `400` error on Claude Sonnet 4.6 and later models, including Claude Sonnet 5. Use structured outputs, system prompt instructions, or `output_config.format` instead.

**Common prefill use cases and migrations:**

**Controlling output formatting** (forcing JSON/YAML output): Use structured outputs or tools with enum fields for classification tasks.

**Eliminating preambles** (removing "Here is..." phrases): Add direct instructions in the system prompt: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc."

**Avoiding bad refusals:** Claude is much better at appropriate refusals now. Clear prompting in the user message without prefill should be sufficient.

**Continuations** (resuming interrupted responses): Move the continuation to the user message: "Your previous response was interrupted and ended with `[previous_response]`. Continue from where you left off."

**Context hydration / role consistency** (refreshing context in long conversations): Inject what were previously prefilled-assistant reminders into the user turn instead.

**Tool parameter JSON escaping may differ**

This is a breaking change when migrating from Sonnet 4.5 or earlier.

JSON string escaping in tool parameters may differ from previous models. Standard JSON parsers handle this automatically, but custom string-based parsing may need updates.

**Extended thinking changes:** `budget_tokens` configurations from Claude Sonnet 4.5 (`thinking: {type: "enabled", budget_tokens: N}`) are not supported on Claude Sonnet 5 and return a 400 error. Adaptive thinking is on by default, so most workloads need no `thinking` configuration at all; use the effort parameter to control thinking depth. If you ran Claude Sonnet 4.5 without extended thinking, pass `thinking: {type: "disabled"}` to preserve that behavior.

**Remove sampling parameters**

This is a breaking change when migrating from Claude 3.x models.

Sampling parameters (`temperature`, `top_p`, `top_k`) set to a non-default value return a 400 error on Claude Sonnet 5. Remove them from requests, and use prompting to guide the model's behavior instead.

**Update tool versions**

This is a breaking change when migrating from Claude 3.x models.

Update to the latest tool versions (`text_editor_20250728`, `code_execution_20260521`). Remove any code using the `undo_edit` command.

**Handle the  refusal stop reason**

Update your application to handle `refusal` stop reasons.

**Update your prompts for behavioral changes**

Claude 4 models have a more concise, direct communication style. Review prompting best practices for optimization guidance.

Claude Haiku 4.5 is the fastest and most intelligent Haiku model with near-frontier performance, delivering premium model quality for interactive applications and high-volume processing.

For a complete overview of capabilities, see the models overview.

For Claude Haiku 4.5 pricing, see Claude pricing.

For significant performance improvements on coding and reasoning tasks, consider enabling extended thinking with `thinking: {type: "enabled", budget_tokens: N}`.

Extended thinking impacts prompt caching efficiency.

Extended thinking is deprecated in Claude 4.6 models and removed in Claude Opus 4.7. If using newer models, use adaptive thinking instead.

**Update your model name:**

```
# From Haiku 3.5
model = "claude-3-5-haiku-20241022"  # Before
model = "claude-haiku-4-5-20251001"  # After
```
**Review new rate limits:** Haiku 4.5 has separate rate limits from Haiku 3.5. See Rate limits documentation for details.

**Explore new capabilities:** See the models overview for details on context awareness, increased output capacity (64k tokens), higher intelligence, and improved speed.

These breaking changes apply when migrating from Claude 3.x Haiku models.

**Update sampling parameters**

This is a breaking change when migrating from Claude 3.x models.

Use only `temperature` OR `top_p`, not both. Setting both returns a 400 error on Claude Haiku 4.5.

**Update tool versions**

This is a breaking change when migrating from Claude 3.x models.

Update to the latest tool versions (`text_editor_20250728`, `code_execution_20250825`). Remove any code using the `undo_edit` command.

**Handle the  refusal stop reason**

Update your application to handle `refusal` stop reasons.

**Update your prompts for behavioral changes**

Claude 4 models have a more concise, direct communication style. Review prompting best practices for optimization guidance.

`claude-haiku-4-5-20251001``text_editor_20250728`, `code_execution_20250825`); legacy versions are not supported`undo_edit` command (if applicable)`temperature` OR `top_p`, not both (setting both returns a 400 error)`refusal` stop reason in your applicationWas this page helpful?

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

- Source: [https://platform.claude.com/docs/en/about-claude/models/migration-guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
