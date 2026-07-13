---
title: "PEFT · Hugging Face"
url: "https://huggingface.co/docs/peft"
library: "huggingface"
created: "2026-07-13T08:58:01.575892+00:00"
---

# Overview

PEFT documentation

PEFT

# PEFT

🤗 PEFT (Parameter-Efficient Fine-Tuning) is a library for efficiently adapting large pretrained models to various downstream applications without fine-tuning all of a model’s parameters because it is prohibitively costly. PEFT methods only fine-tune a small number of (extra) model parameters - significantly decreasing computational and storage costs - while yielding performance comparable to a fully fine-tuned model. This makes it more accessible to train and store large language models (LLMs) on consumer hardware.

PEFT is integrated with the Transformers, Diffusers, and Accelerate libraries to provide a faster and easier way to load, train, and use large models for inference.

Start here if you're new to 🤗 PEFT to get an overview of the library's main features, and how to train a model with a PEFT method.

Practical guides demonstrating how to apply various PEFT methods across different types of tasks like image classification, causal language modeling, automatic speech recognition, and more. Learn how to use 🤗 PEFT with the DeepSpeed and Fully Sharded Data Parallel scripts.

Get a better theoretical understanding of how LoRA and various soft prompting methods help reduce the number of trainable parameters to make training more efficient.

Technical descriptions of how 🤗 PEFT classes and methods work.

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

- Source: [https://huggingface.co/docs/peft](https://huggingface.co/docs/peft)
