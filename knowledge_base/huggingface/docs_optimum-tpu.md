---
title: "🤗 Optimum TPU · Hugging Face"
url: "https://huggingface.co/docs/optimum-tpu"
library: "huggingface"
created: "2026-07-13T08:58:05.881202+00:00"
---

# Overview

Google TPUs documentation

🤗 Optimum TPU

# 🤗 Optimum TPU

**🚧 Optimum-TPU is now archived.**While this project is no longer under development, you can continue exploring TPU solutions with:


- TPU inference for inference
- 🤗 Accelerate for training

Optimum TPU provides all the necessary machinery to leverage and optimize AI workloads running on Google Cloud TPU devices. Optimum-TPU is a HuggingFace solution to optimize HuggingFace products for the TPU platform. This allows users to use HuggingFace features and easy-to-use libraries on TPU with the best performance. We currently optimize transformers and TGI and integrate HuggingFace hub so you can access HuggingFace’s large library of models.

If you are here to start using HuggingFace products on TPU, then you are in the right place

The API provides the overall same user-experience as HuggingFace transformers with the minimum amount of changes required to target performance for inference and training.

Optimum TPU is meant to reduce as much as possible the friction in order to leverage Google Cloud TPU accelerators. As such, we provide a pip installable package to make sure everyone can get easily started.

pip install optimum-tpu -f https://storage.googleapis.com/libtpu-releases/index.html

## Why Choose TPUs

TPUs excel at large-scale machine learning workloads with matrix computations, extended training periods, and large batch sizes. In contrast, GPUs offer more flexibility for models with custom operations or mixed CPU/GPU workloads. TPUs aren’t ideal for workloads needing frequent branching, high-precision arithmetic, or custom training loop operations. More information can be found at https://cloud.google.com/tpu/docs/intro-to-tpu#when_to_use_tpus

## Why Choose Optimum-TPU

Optimum-TPU serves as the bridge between the HuggingFace ecosystem and Google Cloud TPU hardware. It dramatically simplifies what would otherwise be a complex integration process, providing an intuitive interface that abstracts away TPU-specific implementation details while maintaining high performance. Through automated optimizations, efficient batching strategies, intelligent memory management and more, Optimum-TPU ensures your models run at peak efficiency on TPU hardware. The framework’s deep integration with the HuggingFace Hub catalog of models and datasets enables easy deployment and fine-tuning of state-of-the-art models with the familiar ease of use of HuggingFace libraries while maximizing TPU hardware capabilities.

Learn the basics and become familiar with deploying transformers on Google TPUs. Start here if you are using 🤗 Optimum-TPU for the first time!

Practical guides to help you achieve a specific goal. Take a look at these guides to learn how to use 🤗 Optimum-TPU to solve real-world problems.

Deep dives into key concepts behind TPU optimization, architecture, and best practices. Understand how TPUs work and how to maximize their potential.

Technical descriptions of how the classes and methods of 🤗 Optimum-TPU work. Detailed API documentation, configuration options, and implementation details.

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

- Source: [https://huggingface.co/docs/optimum-tpu](https://huggingface.co/docs/optimum-tpu)
