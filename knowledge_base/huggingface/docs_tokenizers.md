---
title: "Tokenizers · Hugging Face"
url: "https://huggingface.co/docs/tokenizers"
library: "huggingface"
created: "2026-07-13T08:57:56.812260+00:00"
---

# Overview

Tokenizers documentation

Tokenizers

Getting started 

API 

# Tokenizers

Fast State-of-the-art tokenizers, optimized for both research and production

🤗 Tokenizers provides an implementation of today’s most used tokenizers, with a focus on performance and versatility. These tokenizers are also used in 🤗 Transformers.

# Main features:

- Train new vocabularies and tokenize, using today’s most used tokenizers.
- Extremely fast (both training and tokenization), thanks to the Rust implementation. Takes less than 20 seconds to tokenize a GB of text on a server’s CPU.
- Easy to use, but also extremely versatile.
- Designed for both research and production.
- Full alignment tracking. Even with destructive normalization, it’s always possible to get the part of the original sentence that corresponds to any token.
- Does all the pre-processing: Truncation, Padding, add the special tokens your model needs.

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

- Source: [https://huggingface.co/docs/tokenizers](https://huggingface.co/docs/tokenizers)
