---
title: "Hugging Face – Posts"
url: "https://huggingface.co/posts"
library: "huggingface"
created: "2026-07-13T08:57:05.986382+00:00"
---

# Overview

Post

  2511

 🔵 VKUE — No GPU? Runs anyway.


"Frontier models need a datacenter GPU" rests on a hidden assumption: that the model reads ALL its parameters every token. Decode is memory-bandwidth bound — sweep 34B params/token and an 8 GB card dies at 1–2 tok/s.


So we ran ONE 34.7B reasoning model — Ourbox-35B-JGOS, a sparse Mixture-of-Experts — as the identical weights across the whole hardware spectrum. All measured:


• B200: 18,057 tok/s (aggregate)

• 1× A10G: 126 tok/s

• 8 GB laptop (RTX 5060): 20 tok/s

• GPU-less CPU: 17 tok/s


Why it works: Ourbox holds 34.7B params but only ~3B are active per token (256 experts, top-8). Since decode is bandwidth-bound, a dense 34B moves ~16.7 GB/token while Ourbox moves ~1.45 GB — ~11× less traffic. Put the experts in system RAM, keep attention/router/shared on the GPU, and a 34.7B reasoner runs on an 8 GB laptop — or no GPU at all.


Sparsity alone, proven (same laptop, same quant, ~same footprint): Ourbox-35B (A3B) 20.01 tok/s vs Qwen2.5-32B (dense) 5.36 → 3.7× from sparsity alone, ~2× the best dense-32B on any 8 GB machine. Not a toy: GPQA Diamond 86.4% (maj@8).


Try it live (same prompt, GPU vs GPU-less CPU, live tok/s). Honest scope: one machine's measurements; the CPU path proves it RUNS without a GPU, not that it beats one.


📝 Article: https://huggingface.co/blog/FINAL-Bench/vkue

🔵 GPU vs CPU demo: https://final-bench-ourbox-35b-vkue-demo.hf.space/

🔵 CPU-only demo: https://final-bench-ourbox-35b-vkue-cpu.hf.space

📊 VKUE leaderboard: FINAL-Bench/VKUE

🤗 Model: FINAL-Bench/Ourbox-35B-JGOS-GGUF

⚡ VKAE (speed): VIDraft/vkae


VKUE is the "runs anywhere" side of our serving line; VKAE the "fast on datacenter GPUs" side. VKAE is fast; VKUE is everywhere.

 "Frontier models need a datacenter GPU" rests on a hidden assumption: that the model reads ALL its parameters every token. Decode is memory-bandwidth bound — sweep 34B params/token and an 8 GB card dies at 1–2 tok/s.

So we ran ONE 34.7B reasoning model — Ourbox-35B-JGOS, a sparse Mixture-of-Experts — as the identical weights across the whole hardware spectrum. All measured:

• B200: 18,057 tok/s (aggregate)

• 1× A10G: 126 tok/s

• 8 GB laptop (RTX 5060): 20 tok/s

• GPU-less CPU: 17 tok/s

Why it works: Ourbox holds 34.7B params but only ~3B are active per token (256 experts, top-8). Since decode is bandwidth-bound, a dense 34B moves ~16.7 GB/token while Ourbox moves ~1.45 GB — ~11× less traffic. Put the experts in system RAM, keep attention/router/shared on the GPU, and a 34.7B reasoner runs on an 8 GB laptop — or no GPU at all.

Sparsity alone, proven (same laptop, same quant, ~same footprint): Ourbox-35B (A3B) 20.01 tok/s vs Qwen2.5-32B (dense) 5.36 → 3.7× from sparsity alone, ~2× the best dense-32B on any 8 GB machine. Not a toy: GPQA Diamond 86.4% (maj@8).

Try it live (same prompt, GPU vs GPU-less CPU, live tok/s). Honest scope: one machine's measurements; the CPU path proves it RUNS without a GPU, not that it beats one.

📝 Article: https://huggingface.co/blog/FINAL-Bench/vkue

🔵 GPU vs CPU demo: https://final-bench-ourbox-35b-vkue-demo.hf.space/

🔵 CPU-only demo: https://final-bench-ourbox-35b-vkue-cpu.hf.space

📊 VKUE leaderboard: FINAL-Bench/VKUE

🤗 Model: FINAL-Bench/Ourbox-35B-JGOS-GGUF

⚡ VKAE (speed): VIDraft/vkae

VKUE is the "runs anywhere" side of our serving line; VKAE the "fast on datacenter GPUs" side. VKAE is fast; VKUE is everywhere.

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

- Source: [https://huggingface.co/posts](https://huggingface.co/posts)
