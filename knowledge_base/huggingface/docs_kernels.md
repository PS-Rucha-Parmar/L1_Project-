---
title: "Kernels · Hugging Face"
url: "https://huggingface.co/docs/kernels"
library: "huggingface"
created: "2026-07-13T08:58:00.379625+00:00"
---

# Overview

Kernels documentation

Kernels

Get started 

Use kernels 

QuickstartUse layersLock kernel versionsEnvironment variablesProjects using kernelsMigrate from older versionsFAQ

Python API 

kernels CLI 

Overviewkernels infokernels versionskernels lockkernels downloadkernels benchmarkkernels verify-signature

Build kernels 

Write kernelsBuild with NixDevelop locallySet up your IDESet up for Metal kernelsDevelop kernels with agentsSecure your kernelsGitHub Actions & HF Jobs

kernel-builder CLI 

Kernel specifications 

Concepts & design 

Resources 

You are viewing main version, which requires installation from source. If you'd like
			regular pip install, checkout the latest stable version (v0.16.0).

# Kernels

The Kernel Hub allows Python libraries and applications to load compute kernels directly from the Hub. Kernels are a first-class repository type on the Hub, with dedicated pages that surface supported hardware and versions. To support dynamic loading, Hub kernels differ from traditional Python kernel packages in that they are made to be:

- **Portable**: a kernel can be loaded from paths outside- `PYTHONPATH`.
- **Unique**: multiple versions of the same kernel can be loaded in the same Python process.
- **Compatible**:- `kernels`must support all recent versions of Python and the different PyTorch build configurations (various CUDA versions and C++ ABIs). Furthermore, older C library versions must be supported.

Browse available kernels at huggingface.co/kernels.

The Kernels project is divided into two parts:

- Builder: `kernel-builder`provides utilities to build, package, and distribute compute kernels in a way that is compatible with the Hugging Face Hub and`kernels`.
- `kernels`: The- `kernels`is a Python package that lets users load compatible compute kernels from the Hub. Refer to the quickstart to know more.

If you’re looking for a more involved “Why kernels?” answer, refer to this page.

The talks page page has links to talks on the Kernels project. The blog page collects blog posts on the Kernels project.

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

- Source: [https://huggingface.co/docs/kernels](https://huggingface.co/docs/kernels)
