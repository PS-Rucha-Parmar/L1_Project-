---
title: "Accelerate · Hugging Face"
url: "https://huggingface.co/docs/accelerate"
library: "huggingface"
created: "2026-07-13T08:58:02.708294+00:00"
---

# Overview

Accelerate documentation

Accelerate

# Accelerate

Accelerate is a library that enables the same PyTorch code to be run across any distributed configuration by adding just four lines of code! In short, training and inference at scale made simple, efficient and adaptable.

```
+ from accelerate import Accelerator
+ accelerator = Accelerator()
+ model, optimizer, training_dataloader, scheduler = accelerator.prepare(
+     model, optimizer, training_dataloader, scheduler
+ )
  for batch in training_dataloader:
      optimizer.zero_grad()
      inputs, targets = batch
      inputs = inputs.to(device)
      targets = targets.to(device)
      outputs = model(inputs)
      loss = loss_function(outputs, targets)
+     accelerator.backward(loss)
      optimizer.step()
      scheduler.step()
```
Built on `torch_xla` and `torch.distributed`, Accelerate takes care of the heavy lifting, so you don’t have to write any custom code to adapt to these platforms.
Convert existing codebases to utilize DeepSpeed, perform fully sharded data parallelism, and have automatic support for mixed-precision training!

To get a better idea of this process, make sure to check out the Tutorials!


This code can then be launched on any system through Accelerate’s CLI interface:

`accelerate launch {my_script.py}`Learn the basics and become familiar with using Accelerate. Start here if you are using Accelerate for the first time!

Practical guides to help you achieve a specific goal. Take a look at these guides to learn how to use Accelerate to solve real-world problems.

High-level explanations for building a better understanding of important topics such as avoiding subtle nuances and pitfalls in distributed training and DeepSpeed.

Technical descriptions of how Accelerate classes and methods work.

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

- Source: [https://huggingface.co/docs/accelerate](https://huggingface.co/docs/accelerate)
