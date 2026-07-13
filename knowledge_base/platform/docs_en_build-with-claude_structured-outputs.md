---
title: "Structured outputs - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/structured-outputs"
library: "platform"
created: "2026-07-13T07:47:06.999389+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Structured outputs constrain Claude's responses to follow a specific schema, ensuring valid, parseable output for downstream processing. Structured outputs provide two complementary features:

`output_config.format`): Get Claude's response in a specific JSON format`strict: true`): Guarantee schema validation on tool names and inputsYou can use these features independently or together in the same request.

Structured outputs are generally available on the Claude API for Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Mythos Preview, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.5, and Claude Haiku 4.5. On Amazon Bedrock, structured outputs are generally available for Claude Opus 4.6, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.5, and Claude Haiku 4.5; Claude Sonnet 5, Claude Opus 4.7, and Claude Mythos Preview are available through Claude in Amazon Bedrock (the Messages-API Bedrock endpoint). Structured outputs are available on Claude Platform on AWS. On Google Cloud, structured outputs are generally available for Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Mythos Preview, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.5, and Claude Haiku 4.5. Structured outputs are generally available on Microsoft Foundry and require a Hosted on Anthropic deployment.

This feature qualifies for Zero Data Retention (ZDR) with limited technical retention. See the Data retention section for details on what is retained and why.

**Migrating from beta?** The `output_format` parameter has moved to `output_config.format`, and beta headers are no longer required. The old beta header (`structured-outputs-2025-11-13`) and `output_format` parameter will continue working for a transition period. See the following code examples for the updated API shape.

Without structured outputs, Claude can generate malformed JSON responses or invalid tool inputs that break your applications. Even with careful prompting, you may encounter:

Structured outputs guarantee schema-compliant responses through constrained decoding:

`JSON.parse()` errorsJSON outputs control Claude's response format, ensuring Claude returns valid JSON matching your schema. Use JSON outputs when you need to:

```
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith ([email protected]) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan_interest": {"type": "string"},
                    "demo_requested": {"type": "boolean"},
                },
                "required": ["name", "email", "plan_interest", "demo_requested"],
                "additionalProperties": False,
            },
        }
    },
)
print(response.content[0].text)
```
**Response format:** Valid JSON matching your schema in `response.content[0].text`

```
{
  "name": "John Smith",
  "email": "[email protected]",
  "plan_interest": "Enterprise",
  "demo_requested": true
}
```
Define your JSON schema

Create a JSON schema that describes the structure you want Claude to follow. The schema uses standard JSON Schema format with some limitations (see JSON Schema limitations).

Add the output_config.format parameter

Include the `output_config.format` parameter in your API request with `type: "json_schema"` and your schema definition.

Parse the response

Claude's response is valid JSON matching your schema, returned in `response.content[0].text`.

The SDKs provide helpers that make it easier to work with JSON outputs, including schema transformation, automatic validation, and integration with popular schema libraries.

The Python SDK's `client.messages.parse()` still accepts `output_format` as a convenience parameter and translates it to `output_config.format` internally. Other SDKs require `output_config` directly. The following examples show the SDK helper syntax.

Instead of writing raw JSON schemas, you can use familiar schema definition tools in your language:

`client.messages.parse()``zodOutputFormat()` or typed JSON Schema literals with `jsonSchemaOutputFormat()``outputConfig(Class<T>)``Anthropic::BaseModel` classes with `output_config: {format: Model}``StructuredOutputModel` with `outputConfig: ['format' => MyClass::class]``Create<T>()` overload, which derives the schema automatically`output_config``output_config````
from pydantic import BaseModel
from anthropic import Anthropic
class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str
    demo_requested: bool
client = Anthropic()
response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith ([email protected]) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_format=ContactInfo,
)
print(response.parsed_output)
```
Each SDK provides helpers that make working with structured outputs easier. See individual SDK pages for full details.

The Python, TypeScript, Ruby, and PHP SDKs automatically transform schemas with unsupported features. The C# and Go SDKs apply the same transformations when the schema is derived from a native type (`Create<T>()` in C#; struct reflection or `BetaJSONSchemaOutputFormat()` on the Go beta API). The transformation steps:

`minimum`, `maximum`, `minLength`, `maxLength`)`additionalProperties: false`This means Claude receives a simplified schema, but your code still enforces all constraints through validation.

**Example:** A Pydantic field with `minimum: 100` becomes a plain integer in the sent schema, but the SDK updates the description to "Must be at least 100" and validates the response against the original constraint.

For enforcing JSON Schema compliance on tool inputs with grammar-constrained sampling, see Strict tool use.

JSON outputs and strict tool use solve different problems and work together:

When combined, Claude can call tools with guaranteed-valid parameters AND return structured JSON responses. This is useful for agentic workflows where you need both reliable tool calls and structured final outputs.

```
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Help me plan a trip to Paris departing May 15, 2026",
        }
    ],
    # JSON outputs: structured response format
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "next_steps"],
                "additionalProperties": False,
            },
        }
    },
    # Strict tool use: guaranteed tool parameters
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["destination", "date"],
                "additionalProperties": False,
            },
        }
    ],
)
print(response)
```
Structured outputs use constrained sampling with compiled grammar artifacts. This introduces some performance characteristics to be aware of:

`name` or `description` fields does not invalidate the cacheWhen using structured outputs, Claude automatically receives an additional system prompt explaining the expected output format. This means:

`output_config.format` parameter will invalidate any prompt cache for that conversation threadStructured outputs support standard JSON Schema with some limitations. Both JSON outputs and strict tool use share these limitations.

The Python, TypeScript, Ruby, and PHP SDKs can automatically transform schemas with unsupported features by removing them and adding constraints to field descriptions. The C# and Go SDKs do the same when the schema is derived from a native type. See SDK-specific methods for details.

When using structured outputs, properties in objects maintain their defined ordering from your schema, with one important caveat: **required properties appear first, followed by optional properties**.

For example, given this schema:

```
{
  "type": "object",
  "properties": {
    "notes": { "type": "string" },
    "name": { "type": "string" },
    "email": { "type": "string" },
    "age": { "type": "integer" }
  },
  "required": ["name", "email"],
  "additionalProperties": false
}
```
The output will order properties as:

`name` (required, in schema order)`email` (required, in schema order)`notes` (optional, in schema order)`age` (optional, in schema order)This means the output might look like:

```
{
  "name": "John Smith",
  "email": "[email protected]",
  "notes": "Interested in enterprise plan",
  "age": 35
}
```
If property order in the output is important to your application, mark all properties as required, or account for this reordering in your parsing logic.

While structured outputs guarantee schema compliance in most cases, there are scenarios where the output may not match your schema:

**Refusals** (`stop_reason: "refusal"`)

Claude maintains its safety and helpfulness properties even when using structured outputs. If Claude refuses a request for safety reasons:

`stop_reason: "refusal"`**Token limit reached** (`stop_reason: "max_tokens"`)

If the response is cut off due to reaching the `max_tokens` limit:

`stop_reason: "max_tokens"``max_tokens` value to get the complete structured output**Enum value casing**

Structured outputs don't guarantee the capitalization of string `enum` and `const` values: Claude may return a value that differs from your schema only in capitalization, typically in the first letter of a word following a space. For example, given this schema:

```
{
  "type": "string",
  "enum": ["Conversation Topic 1", "Conversation Topic 2", "Conversation topic 3"]
}
```
The output may contain `"Conversation Topic 3"` (capital "T") even though that exact value isn't in the enum. The response completes normally, with no error and no special `stop_reason`. This applies to both JSON outputs and strict tool use. Compare enum values case-insensitively, and avoid enum values that differ only in capitalization.

Structured outputs work by compiling your JSON schemas into a grammar that constrains Claude's output. More complex schemas produce larger grammars that take longer to compile. To protect against excessive compilation times, the API enforces several complexity limits.

The following limits apply to all requests with `output_config.format` or `strict: true`:

| Limit | Value | Description | 
|---|---|---|
| Strict tools per request | 20 | Maximum number of tools with `strict: true`. Non-strict tools don't count toward this limit. | 
| Optional parameters | 24 | Total optional parameters across all strict tool schemas and JSON output schemas. Each parameter not listed in `required`counts toward this limit. | 
| Parameters with union types | 16 | Total parameters that use `anyOf`or type arrays (for example,`"type": ["string", "null"]`) across all strict schemas. These are especially expensive because they create exponential compilation cost. | 

These limits apply to the combined total across all strict schemas in a single request. For example, if you have 4 strict tools with 6 optional parameters each, you'll reach the 24-parameter limit even though no single tool seems complex.

Beyond the explicit limits in the preceding table, there are additional internal limits on the compiled grammar size. These limits exist because schema complexity doesn't reduce to a single dimension: features like optional parameters, union types, nested objects, and number of tools interact with each other in ways that can make the compiled grammar disproportionately large.

When these limits are exceeded, you'll receive a 400 error with the message "Schema is too complex for compilation." These errors mean the combined complexity of your schemas exceeds what can be efficiently compiled, even if each individual limit in the preceding table is satisfied. As a final stop-gap, the API also enforces a **compilation timeout of 180 seconds**. Schemas that pass all explicit checks but produce very large compiled grammars may hit this timeout.

If you're hitting complexity limits, try these strategies in order:

**Mark only critical tools as strict.** If you have many tools, reserve it for tools where schema violations cause real problems, and rely on Claude's natural adherence for simpler tools.

**Reduce optional parameters.** Make parameters `required` where possible. Each optional parameter roughly doubles a portion of the grammar's state space. If a parameter always has a reasonable default, consider making it required and having Claude provide that default explicitly.

**Simplify nested structures.** Deeply nested objects with optional fields compound the complexity. Flatten structures where possible.

**Split into multiple requests.** If you have many strict tools, consider splitting them across separate requests or sub-agents.

For persistent issues with valid schemas, contact support with your schema definition.

Prompts and responses are processed with ZDR when using structured outputs. However, the JSON schema itself is temporarily cached for up to 24 hours since last use for optimization purposes. No prompt or response data is retained beyond the API response.

Structured outputs are HIPAA eligible, but **PHI must not be included in JSON schema definitions**. The API compiles JSON schemas into grammars that are cached separately from message content, and these cached schemas do not receive the same PHI protections as prompts and responses. Do not include PHI in schema property names, `enum` values, `const` values, or `pattern` regular expressions. PHI should only appear in message content (prompts and responses), where it is protected under HIPAA safeguards.

For ZDR and HIPAA eligibility across all features, see API and data retention.

**Works with:**

`output_config.format`) and strict tool use (`strict: true`) together in the same request**Incompatible with:**

`output_config.format`.**Grammar scope:** Grammars apply only to Claude's direct output, not to tool use calls, tool results, or thinking tags (when using Extended Thinking). Grammar state resets between sections, allowing Claude to think freely while still producing structured output in the final response.

Have Claude cite its sources when answering questions about provided documents.

Enforce JSON Schema compliance on Claude's tool inputs with grammar-constrained sampling.

Connect Claude to external tools and APIs. Learn where tools execute and how the agentic loop works.

Learn about Anthropic's pricing structure for models and features.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/structured-outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
