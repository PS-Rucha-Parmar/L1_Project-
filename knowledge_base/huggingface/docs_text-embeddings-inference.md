---
title: "Text Embeddings Inference · Hugging Face"
url: "https://huggingface.co/docs/text-embeddings-inference"
library: "huggingface"
created: "2026-07-13T08:57:48.759087+00:00"
---

# Overview

text-embeddings-inference documentation

Text Embeddings Inference

Getting started 

Tutorials 

Using TEI locally with CPUUsing TEI locally with MetalUsing TEI locally with GPUServing private and gated modelsBuild custom container for TEIUsing TEI container with Intel HardwareUsing TEI on AMD Instinct GPUs (ROCm)Example uses

Deploying TEI on Google Cloud 

Reference 

# Text Embeddings Inference

Text Embeddings Inference (TEI) is a comprehensive toolkit designed for efficient deployment and serving of open source text embeddings models. It enables high-performance extraction for the most popular models, including FlagEmbedding, Ember, GTE, and E5.

TEI offers multiple features tailored to optimize the deployment process and enhance overall performance.

**Key Features:**

- **Streamlined Deployment:**TEI eliminates the need for a model graph compilation step for an easier deployment process.
- **Efficient Resource Utilization:**Benefit from small Docker images and rapid boot times, allowing for true serverless capabilities.
- **Dynamic Batching:**TEI incorporates token-based dynamic batching thus optimizing resource utilization during inference.
- **Optimized Inference:**TEI leverages Flash Attention, Candle, and cuBLASLt by using optimized transformers code for inference.
- **Safetensors weight loading:**TEI loads Safetensors weights for faster boot times.
- **Production-Ready:**TEI supports distributed tracing through Open Telemetry and exports Prometheus metrics.

**Benchmarks**

Benchmark for BAAI/bge-base-en-v1.5 on an NVIDIA A10 with a sequence length of 512 tokens:



**Getting Started:**

To start using TEI, check the Quick Tour guide.

Update on GitHub

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

- Source: [https://huggingface.co/docs/text-embeddings-inference](https://huggingface.co/docs/text-embeddings-inference)
