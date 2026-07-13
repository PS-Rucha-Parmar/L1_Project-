---
title: "Feature Selection Techniques in Machine Learning - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/machine-learning/feature-selection-techniques-in-machine-learning"
library: "geeksforgeeks"
created: "2026-07-13T08:04:28.561081+00:00"
---

# Overview

Feature selection is the process of choosing only the most useful input features for a machine learning model. It helps improve model performance, reduces noise and makes results easier to understand.

- Helps remove irrelevant and redundant features
- Improves accuracy and reduces overfitting
- Speeds up model training
- Makes models simpler and easier to interpret

### Need of Feature Selection

Feature selection methods are essential in data science and machine learning for several key reasons:

- **Improved Accuracy**
- **Faster Training**
- **Greater Interpretability**
- **Avoiding the Curse of Dimensionality**

## Types of Feature Selection Methods

There are various algorithms used for feature selection and are grouped into three main categories and each one has its own strengths and trade-offs depending on the use case.

### 1. Filter Methods

Filter methods evaluate each feature independently with respect to the target variable. Features are selected based on statistical measures that indicate their relevance to the target. These methods are commonly used in the preprocessing phase to remove irrelevant or redundant features.

- Do not rely only on correlation
- Use different statistical techniques depending on data type
- Fast and model-independent feature selection approach

**Common Filter Techniques**

- **Information Gain**- **:**
- **Chi-square test**- **:**
- **Fisher’s Score:**
- **Pearson’s Correlation Coefficient**- **:**
- **Variance Threshold**- **:**
- **Mean Absolute Difference**- **:**
- **Dispersion ratio**- **:**

**Advantages**

- **Fast and efficient**
- **Easy to implement**
- **Model Independence**

**Limitations**

- **Limited interaction with the model**
- **Choosing the right metric**

### 2. Wrapper methods

Wrapper methods are feature selection techniques that evaluate different combinations of features by measuring their impact on model performance. They use search strategies to add or remove features and select the optimal subset based on predefined stopping criteria.

- Evaluates feature subsets using a machine learning model
- Uses greedy or non-greedy search strategies
- Measures the relationship between feature subsets and the target variable
- Adds or removes features based on model performance
- Stops when performance decreases or the desired number of features is reached

**Common Wrapper Techniques**

- **Forward Selection**- **:**
- **Backward Elimination**- **:**
- **Recursive Feature Elimination (RFE)**- **:**

### Advantages

- **Model-specific optimization**
- **Flexible**

### Limitations

- **Computationally expensive**
- **Risk of overfitting**

### 3. Embedded methods

Embedded methods perform feature selection during the model training process. They combine the benefits of both filter and wrapper methods. Feature selection is integrated into the model training allowing the model to select the most relevant features based on the training process dynamically.

**Common Embedded Techniques**

- **L1 Regularization (Lasso)**- **:**
- **Decision Trees**- **Random Forests**- **:**
- **Gradient Boosting**- **:**

**Advantages**

- **Efficient and effective**
- **Model-specific learning**

**Limitations**

- **Limited interpretability**
- **Not universally applicable**

## Choosing the Right Feature Selection Method

Choice of feature selection method depends on several factors:

- **Dataset size**
- **Model type**
- **Interpretability**
- **Computational resources:**

With these feature selection methods we can easily improve performance of our model and reduce its computational cost.

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

- Source: [https://www.geeksforgeeks.org/machine-learning/feature-selection-techniques-in-machine-learning](https://www.geeksforgeeks.org/machine-learning/feature-selection-techniques-in-machine-learning)
