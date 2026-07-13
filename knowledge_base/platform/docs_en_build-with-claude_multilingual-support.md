---
title: "Multilingual support - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/multilingual-support"
library: "platform"
created: "2026-07-13T08:01:51.278892+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Claude demonstrates robust multilingual capabilities, with particularly strong performance in zero-shot tasks across languages. The model maintains consistent relative performance across both widely spoken and lower-resource languages, making it a reliable choice for multilingual applications.

Claude is capable in many languages beyond those benchmarked in the following table. Test with any languages relevant to your specific use cases.

The following table shows zero-shot chain-of-thought evaluation scores for Claude models across languages, expressed as a percentage relative to English performance (100%):

| Language | Claude Opus 4.1 (deprecated) 1 | Claude Sonnet 4.5 1 | Claude Haiku 4.5 1 | 
|---|---|---|---|
| English (baseline, fixed to 100%) | 100% | 100% | 100% | 
| Spanish | 98.1% | 98.2% | 96.4% | 
| Portuguese (Brazil) | 97.8% | 97.8% | 96.1% | 
| Italian | 97.7% | 97.9% | 96.0% | 
| French | 97.9% | 97.5% | 95.7% | 
| Indonesian | 97.3% | 97.3% | 94.2% | 
| German | 97.7% | 97.0% | 94.3% | 
| Arabic | 97.1% | 97.2% | 92.5% | 
| Chinese (Simplified) | 97.1% | 96.9% | 94.2% | 
| Korean | 96.6% | 96.7% | 93.3% | 
| Japanese | 96.9% | 96.8% | 93.5% | 
| Hindi | 96.8% | 96.7% | 92.4% | 
| Bengali | 95.7% | 95.4% | 90.4% | 
| Swahili | 89.8% | 91.1% | 78.3% | 
| Yoruba | 80.3% | 79.7% | 52.7% | 

1 With extended thinking.

These metrics are based on MMLU (Massive Multitask Language Understanding) English test sets that were translated into 14 additional languages by professional human translators, as documented in OpenAI's simple-evals repository. The use of human translators for this evaluation ensures high-quality translations, particularly important for languages with fewer digital resources.

Claude infers the response language from the conversation, but for production applications you should state the target language explicitly. The most reliable place to do this is the system prompt, which keeps the instruction stable across every turn of a conversation.

```
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    system="Always respond in French, regardless of the language the user writes in.",
    messages=[{"role": "user", "content": "How do I reset my password?"}],
)
print(message.content)
```
If your application lets users pick a language at runtime, interpolate that choice into the system prompt rather than relying on Claude to infer it from the user's message. To translate between two specific languages, name both: `Translate the user's message from German to Korean. Respond with only the translation.`

When working with multilingual content:

Also follow the general guidance in Prompt engineering overview to further improve output quality.

Apply general prompting techniques to improve multilingual output quality.

Build a localized support chatbot using a language-constrained system prompt.

Compare model tiers to balance multilingual quality against cost and latency.

Evaluate translation and localization quality before you ship.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/multilingual-support](https://platform.claude.com/docs/en/build-with-claude/multilingual-support)
