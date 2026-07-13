---
title: "Feature Engineering - Scaling, Normalization and Standardization - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/machine-learning/feature-engineering-scaling-normalization-and-standardization"
library: "geeksforgeeks"
created: "2026-07-13T08:04:58.984357+00:00"
---

# Overview

Well-designed Feature engineering is the process of creating, transforming or selecting important features from raw data to improve model performance. These features help the model capture useful patterns and relationships in the data.

It contributes to model building in the following ways:

- Well-designed features help the model to learn complex patterns more effectively.
- Removing noise and irrelevant information improves model prediction accuracy.
- Focusing on meaningful features helps the model to generalize better and reduces overfitting.
- Clear and informative features make the model easier to understand and interpret.

## 1. Absolute Maximum Scaling

Absolute Maximum Scaling is a feature scaling method where each value is divided by the maximum absolute value of that feature. This transformation rescales the data so that values fall within the range of −1 to 1.

- **Sensitive to Outliers:**
- **Best for Clean Data:**

**Scaling Formula: **

**Scaling Formula:**


X_{\rm {scaled }}=\frac{X_{i}}{\rm{max}\left(|X|\right)} 

**Implementation**

**Implementation**

Dataset can be downloaded from here.


**Step 1: Import Libraries and Dataset**

import pandas as pd
import numpy as np
df = pd.read_csv('Housing.csv')
df = df.select_dtypes(include=np.number)
df.head()

**Output:**

**Step 2: Apply Absolute Maximum Scaling**

- **np.max(np.abs(df), axis=0)**
- **df / max_abs**
- **scaled_df.head()**

max_abs = np.max(np.abs(df), axis=0)
scaled_df = df / max_abs
scaled_df.head()

**Output:**

## 2. Min-Max Scaling

Min-Max Scaling rescales features by subtracting the minimum value and dividing by the difference between the maximum and minimum values. This usually maps feature values to the range 0 to 1 while preserving the original distribution.

**Scaling Formula: **

**Scaling Formula:**


X_{\rm {scaled }}=\frac{X_{i}-X_{\text {min}}}{X_{\rm{max}} - X_{\rm{min}}} 

**Implementation**

**Implementation**

- **MinMaxScaler():**
- **scaler.fit_transform(df):**

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_data, columns=df.columns)
scaled_df.head()

**Output:**

## 3. Normalization (Vector Normalization)

Normalization scales each data sample so that its vector length (Euclidean norm) becomes 1. It focuses on the direction of data points rather than their magnitude, making it useful in tasks like text classification and clustering.

### Scaling Formula:


X_{\text{scaled}} = \frac{X_i}{\| X \|} 

**Where:**

- {X_i} is each individual value.
- {\| X \|} represents the Euclidean norm (or length) of the vector- X .
- Normalizes each sample to unit length.
- Useful for direction-based similarity metrics.

**I**

**I**

- **Normalizer():**
- **scaler.fit_transform(df):**

from sklearn.preprocessing import Normalizer
scaler = Normalizer()
scaled_data = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_data, columns=df.columns)
scaled_df.head()

**Output:**

## 4. Standardization

Standardization scales features by subtracting the mean and dividing by the standard deviation. This transforms the data so that features have zero mean and unit variance, which helps many machine learning models perform better.

### Scaling Formula:


X_{\rm {scaled }}=\frac{X_{i}-\mu}{\sigma} 

- where \mu = mean,\sigma = standard deviation.
- Produces features with mean 0 and variance 1.
- Effective for data approximately normally distributed.

**I**

**I**

- **standardScaler()**
- **scaler.fit_transform(df)**

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_data,
                         columns=df.columns)
print(scaled_df.head())

**Output:**

## 5. Robust Scaling

Robust Scaling scales features using the median and interquartile range (IQR) instead of the mean and standard deviation. This makes it less sensitive to outliers and skewed data, making it suitable for datasets with extreme values or noise.

### Scaling Formula:


X_{\rm {scaled }}=\frac{X_{i}-X_{\text {median }}}{IQR} 

**I**

**I**

- **RobustScaler()**
- **scaler.fit_transform(df)**

from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
scaled_data = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_data,
                         columns=df.columns)
print(scaled_df.head())

**Output:**

## Comparison of Various Feature Scaling Techniques

Let's see the key differences across the five main feature scaling techniques commonly used in machine learning preprocessing.

| Type | Method Description | Sensitivity to Outliers | Typical Use Cases | 
|---|---|---|---|
| Absolute Maximum Scaling | Divides values by max absolute value in each feature | High | Sparse data, simple scaling | 
| Min-Max Scaling (Normalization) | Scales features to by min-max normalization | High | Neural networks, bounded input features | 
| Normalization (Vector Norm) | Scales each sample vector to unit length (norm = 1) | Not applicable (per row) | Direction-based similarity, text classification | 
| Standardization (Z-Score) | Centers features to mean 0 and scales to unit variance | Moderate | Most ML algorithms, assumes approx. normal data | 
| Robust Scaling | Centers on median and scales using IQR | Low | Data with outliers, skewed distributions | 

## Advantages

- **Improves Model Performance:**
- **Speeds Up Convergence:**
- **Prevents Feature Bias:**
- **Increases Numerical Stability:**
- **Facilitates Algorithm Compatibility:**

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

- Source: [https://www.geeksforgeeks.org/machine-learning/feature-engineering-scaling-normalization-and-standardization](https://www.geeksforgeeks.org/machine-learning/feature-engineering-scaling-normalization-and-standardization)
