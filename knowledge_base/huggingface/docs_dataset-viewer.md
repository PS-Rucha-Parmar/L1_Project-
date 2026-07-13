---
title: "🤗 Dataset viewer · Hugging Face"
url: "https://huggingface.co/docs/dataset-viewer"
library: "huggingface"
created: "2026-07-13T08:57:42.990860+00:00"
---

# Overview

Dataset viewer documentation

🤗 Dataset viewer

# 🤗 Dataset viewer

The dataset page includes a table with the dataset’s contents, arranged by pages of 100 rows. You can navigate between pages using the buttons at the bottom of the table, filter, search, look at basic statistics, and more.

Dataset viewer of the OpenBookQA dataset

## Contents of the documentation

These documentation pages are focused on the **dataset viewer’s backend** (code in https://github.com/huggingface/dataset-viewer), which provides the table with pre-computed data through an API for all the datasets on the Hub. You can explore the sections if you want to consume the API for your application or to understand how we preprocess the datasets.

Otherwise, if you want to learn about creating datasets from the Hub’s web-based interface, **configuring the dataset viewer** for data, images, or audio, or fixing errors, you might prefer reading the Datasets Hub documentation pages. Take also a look to the example datasets collections: splits configuration, subsets configuration, CSV data files and image datasets.

## Dataset viewer’s backend

The dataset viewer’s backend provides an API for visualizing and exploring all types of datasets - computer vision, speech, text, and tabular - stored on the Hugging Face Hub.

The main feature of the dataset viewer’s backend is to auto-convert all the Hub datasets to Parquet. Read more in the Parquet section.

As datasets increase in size and data type richness, the cost of preprocessing (storage and compute) these datasets can be challenging and time-consuming. To help users access these modern datasets, The dataset viewer runs a server behind the scenes to generate the API responses ahead of time and stores them in a database so they are instantly returned when you make a query through the API.

Let the dataset viewer take care of the heavy lifting so you can use a simple **REST API** on any of the **100,000+ datasets on Hugging Face** to:

- List the **dataset splits, column names and data types**
- Get the **dataset size**(in number of rows or bytes)
- Download and view **rows at any index**in the dataset
- **Search**a word in the dataset
- **Filter**rows based on a query string
- Get insightful **statistics**about the data
- Access the dataset as **parquet files**to use in your favorite**processing or analytics framework**

Join the growing community on the forum or Discord today, and give the dataset viewer repository a ⭐️ if you’re interested in the latest updates!

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

- Source: [https://huggingface.co/docs/dataset-viewer](https://huggingface.co/docs/dataset-viewer)
