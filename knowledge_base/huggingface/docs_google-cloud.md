---
title: "Hugging Face on Google Cloud · Hugging Face"
url: "https://huggingface.co/docs/google-cloud"
library: "huggingface"
created: "2026-07-13T08:57:50.973814+00:00"
---

# Overview

Google Cloud documentation

Hugging Face on Google Cloud

# Hugging Face on Google Cloud

Hugging Face collaborates with Google across open science, open source, cloud, and hardware to enable companies to build their own AI with the latest open models from Hugging Face and the latest cloud and hardware features from Google Cloud.

Hugging Face enables new experiences for Google Cloud customers. They can easily train and deploy Hugging Face models on Google Kubernetes Engine (GKE), Vertex AI, or Cloud Run on any hardware available in Google Cloud using Hugging Face Deep Learning Containers (DLCs).

If you have any issues using Hugging Face on Google Cloud, you can get community support by creating a new topic in the Forum dedicated to Google Cloud usage.

## Train and Deploy Models on Google Cloud with Hugging Face Deep Learning Containers

Hugging Face built Deep Learning Containers (DLCs) for Google Cloud customers to run any of their machine learning workload in an optimized environment, with no configuration or maintenance on their part. These are Docker images pre-installed with deep learning frameworks and libraries such as 🤗 Transformers, 🤗 Datasets, and 🤗 Tokenizers. The DLCs allow you to directly serve and train any models, skipping the complicated process of building and optimizing your serving and training environments from scratch.

For training, our DLCs are available for PyTorch via 🤗 Transformers. They include support for training on both GPUs and TPUs with libraries such as 🤗 TRL, Sentence Transformers, or 🧨 Diffusers.

For inference, we have a general-purpose PyTorch inference DLC, for serving models trained with any of those frameworks mentioned before on both CPU and GPU. There is also the Text Generation Inference (TGI) DLC for high-performance text generation of LLMs on both GPU and TPU. Finally, there is a Text Embeddings Inference (TEI) DLC for high-performance serving of embedding models on both CPU and GPU.

The DLCs are hosted in Google Cloud Artifact Registry and can be used from any Google Cloud service such as Google Kubernetes Engine (GKE), Vertex AI, or Cloud Run.

Hugging Face DLCs are open source and licensed under Apache 2.0 within the Google-Cloud-Containers repository. For premium support, our Expert Support Program gives you direct dedicated support from our team.

You have two options to take advantage of these DLCs as a Google Cloud customer:

- To get started, you can use our no-code integrations within Vertex AI or GKE.
- For more advanced scenarios, you can pull the containers from the Google Cloud Artifact Registry directly in your environment. Here is a list of notebooks examples.

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

- Source: [https://huggingface.co/docs/google-cloud](https://huggingface.co/docs/google-cloud)
