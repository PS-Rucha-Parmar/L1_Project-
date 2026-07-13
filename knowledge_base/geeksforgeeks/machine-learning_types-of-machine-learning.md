---
title: "Types of Machine Learning - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/machine-learning/types-of-machine-learning"
library: "geeksforgeeks"
created: "2026-07-13T08:00:04.879861+00:00"
---

# Overview

Machine Learning (ML) is a subfield of Artificial Intelligence (AI) that focuses on building algorithms and models that enable computers to learn from data and improve with experience without explicit programming for every task. In simple words, Machine Learning teaches systems to learn patterns and make decisions like humans by analyzing and learning from data.

There are several types of machine learning, each with special characteristics and applications. Some of the main types of machine learning algorithms are as follows:

- Supervised Machine Learning
- Unsupervised Machine Learning
- Reinforcement Learning

Additionally, there is a more specific category called Semi-Supervised Learning and Self-Supervised Learning, which combines elements of both supervised and unsupervised learning

## 1. Supervised Machine Learning

Supervised learning is defined as when a model gets trained on a "Labeled Dataset". Labelled datasets have both input and output parameters. In Supervised Learning algorithms learn to map points between inputs and correct outputs. It has both training and validation datasets labelled.

** Example: **If you train a model using labeled images of cats and dogs, it learns the features of each. When shown a new image, it predicts whether it’s a cat or a dog.

There are two main categories of supervised learning that are mentioned below:

### 1. Classification

Classification predicts categorical outputs, meaning it assigns data into predefined classes like spam/non-spam emails or disease risk categories. These algorithms learn to map input features to discrete labels. Here are some classification algorithms:

- Logistic Regression
- Decision Tree
- Random Forest
- K-Nearest Neighbors (KNN)
- Naive Bayes
- Support Vector Machine

### 2. Regression

Regression, predicts continuous values, such as house prices or product sales. It learns the relationship between input features and a numerical target variable. Here are some regression algorithms:

### Where to Use Supervised Learning

- When you have labeled data and want to predict outcomes.
- Ideal for classification (like spam detection) or regression tasks (like price forecasting).
- Best used in domains where historical data with outcomes is already available.

### Applications

Supervised learning is used in a wide variety of applications, including:

- **Image, speech and text processing:**
- **Predictive analytics:**
- **Recommendation and personalization:**
- **Healthcare and finance:**
- **Automation and control:**

## 2. Unsupervised Machine Learning

Unsupervised Learning works with unlabeled data, meaning there are no predefined outputs. The algorithm finds hidden patterns, groups or relationships within the data on its own. It’s mainly used for clustering, dimensionality reduction and data visualization.

** Example: **If you have customer data without labels, the algorithm can group similar customers based on purchase behavior useful for segmentation and marketing.

There are two main categories of unsupervised learning that are mentioned below:

### 1. Clustering

Clustering is the process of grouping data points into clusters based on their similarity. This technique is useful for identifying patterns and relationships in data without the need for labeled examples. Common techniques include:

**2. Dimensionality Reduction Techniques**

**2. Dimensionality Reduction Techniques**

Dimensionality reduction helps reduce the number of features while preserving important information. Common techniques include:

### 3. Association Rule Learning

Association rule learning is a technique for discovering relationships between items in a dataset. It identifies rules that indicate the presence of one item implies the presence of another item with a specific probability. Common techniques include:

### Where to Use Unsupervised Learning

- When data is unlabeled or unstructured.
- Useful for exploratory analysis, clustering or feature extraction.
- Common in marketing, recommendation systems and fraud detection where patterns matter more than labels.

### Applications of Unsupervised Learning

Here are some common applications of unsupervised learning:

- **Clustering and segmentation:**
- **Anomaly detection:**
- **Dimensionality reduction:**
- **Recommendation and marketing:**
- **Data preprocessing and analysis:**

## 3. Reinforcement Learning

Reinforcement learning trains an agent to make a sequence of decisions through trial and error. The agent interacts with the environment, receives feedback in the form of rewards or penalties and learns optimal actions over time.

** Example: **An AI agent learning to play chess gets positive feedback for good moves and negative for poor ones. Over time, it learns strategies to win more often.

Here are some of most common reinforcement learning algorithms:

- **Q-learning:**
- **SARSA (State-Action-Reward-State-Action):**
- **Deep Q-learning**- **:**

### Types of Reinforcement Learning

- **Positive Reinforcement:**
- **Negative Reinforcement:**

### Where to Use Reinforcement Learning

- When you need an agent to learn by interacting with an environment.
- Best for decision-making or optimization tasks involving trial and feedback loops.
- Used when long-term performance or adaptive behavior is more important than immediate accuracy.

### Applications of Reinforcement Learning

Here are some applications of reinforcement learning:

- **Gaming and simulation:**
- **Robotics and automation:**
- **Autonomous vehicles:**
- **Healthcare and finance:**
- **Recommendation and personalization:**
- **Industrial and energy management:**

## Semi-Supervised Learning: Supervised + Unsupervised Learning

Semi-Supervised learning Semi-Supervised Learning combines both Supervised and Unsupervised approaches. It uses a small set of labeled data and a large set of unlabeled data for training useful when labeling is costly or time-consuming.

** Example**: Consider that we are building a language translation model, having labeled translations for every sentence pair can be resources intensive. It allows the models to learn from labeled and unlabeled sentence pairs, making them more accurate. This technique has led to significant improvements in the quality of machine translation services.

### Popular Techniques

- **Graph-based Learning:**
- **Label Propagation:**
- **Co-training**- **:**
- **Self-training**- **:**
- **Generative Adversarial Networks (GANs)**- **:**

### Where to Use Semi-Supervised Learning

- When you have limited labeled data but plenty of unlabeled data.
- Useful for domains with high labeling costs, such as medical, NLP or image datasets.
- Ideal when unlabeled data still holds valuable information that can improve learning performance.

### Applications

- **Image Classification:**
- **Natural Language Processing (NLP):**
- **Speech Recognition:**
- **Recommendation Systems:**
- **Healthcare & Medical Imaging:**

## Self-Supervised Learning

Self-Supervised Learning (SSL) is a modern approach where models generate their own labels from raw data. It doesn’t rely on manual annotation instead, the model learns by predicting parts of data from other parts.

** Example:** In NLP, models like BERT or GPT learn by predicting masked words in sentences, using surrounding context as supervision. This helps them learn language understanding without human labeling.

### Popular Techniques

- Masked Modeling (BERT)
- Contrastive Learning (SimCLR, MoCo)
- Autoencoders
- Predictive Coding

### Applications

- Natural Language Processing
- Computer Vision and Speech Recognition
- Video understanding
- Pre-training for large AI models

### Where to Use Self-Supervised Learning

- When manual labeling is impossible or expensive.
- Suitable for large-scale datasets like text, audio and images.
- Best for pre-training models that can later be fine-tuned for specific supervised tasks.

## Comparison

| Type | Data Requirement | Label Availability | Learning Goal | Common Use Case | 
|---|---|---|---|---|
| Supervised | High | Labeled | Predict outputs | Spam detection, Price prediction | 
| Unsupervised | Medium | Unlabeled | Find hidden patterns | Customer segmentation | 
| Reinforcement | High | Reward feedback | Learn best actions | Robotics, Games | 
| Semi-Supervised | Medium | Partial labels | Combine both learning types | NLP, Image recognition | 
| Self-Supervised | High | Self-generated labels | Learn data representations | BERT, GPT, CLIP | 


: Machine Learning AlgorithmsMust check, our detailed article on

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

- Source: [https://www.geeksforgeeks.org/machine-learning/types-of-machine-learning](https://www.geeksforgeeks.org/machine-learning/types-of-machine-learning)
