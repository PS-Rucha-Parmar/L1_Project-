---
title: "Data Preprocessing in Python - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/data-analysis/data-preprocessing-machine-learning-python"
library: "geeksforgeeks"
created: "2026-07-13T08:01:37.406252+00:00"
---

# Overview

Data preprocessing is the first step in any data analysis or machine learning pipeline. It involves cleaning, transforming and organizing raw data to ensure it is accurate, consistent and ready for modeling. It has a big impact on model building such as:

- Clean and well-structured data allows models to learn meaningful patterns rather than noise.
- Properly processed data prevents misleading inputs, leading to more reliable predictions.
- Organized data makes it simpler to create useful inputs for the model, enhancing model performance.
- Organized data supports better Exploratory Data Analysis (EDA), making patterns and trends more interpretable.

## Steps-by-Step implementation

Let's implement various preprocessing features,

### Step 1: Import Libraries and Load Dataset

We prepare the environment with libraries like pandas, numpy, scikit learn, matplotlib and seaborn for data manipulation, numerical operations, visualization and scaling. Load the dataset for preprocessing.

The sample dataset can be downloaded from here.


import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt
df = pd.read_csv('Geeksforgeeks/Data/diabetes.csv')
df.head()

**Output:**

### Step 2: Inspect Data Structure and Check Missing Values

We understand dataset size, data types and identify any incomplete (missing) data that needs handling.

- **df.info():**
- **df.isnull().sum():**

df.info()
print(df.isnull().sum())

**Output:**

### Step 3: Statistical Summary and Visualizing Outliers

Get numeric summaries like mean, median, min/max and detect unusual points (outliers). Outliers can skew models if not handled.

- **df.describe():**
- **Boxplots:**

df.describe()
fig, axs = plt.subplots(len(df.columns), 1, figsize=(7, 18), dpi=95)
for i, col in enumerate(df.columns):
    axs[i].boxplot(df[col], vert=False)
    axs[i].set_ylabel(col)
plt.tight_layout()
plt.show()

**Output: **

### Step 4: Remove Outliers Using the Interquartile Range (IQR) Method

Remove extreme values beyond a reasonable range to improve model robustness.

- IQR = Q3 (75th percentile) – Q1 (25th percentile).
- Values below Q1 - 1.5IQR or above Q3 + 1.5IQR are outliers.
- Calculate lower and upper bounds for each column separately.
- Filter data points to keep only those within bounds.

q1, q3 = np.percentile(df['Insulin'], [25, 75])
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
clean_df = df[(df['Insulin'] >= lower) & (df['Insulin'] <= upper)]


In practice, outlier removal should be applied across all relevant numerical columns to ensure consistent preprocessing.Note:

### Step 5: Correlation Analysis

Understand relationships between features and the target variable (Outcome). Correlation helps gauge feature importance.

- **df.corr():**
- Heatmap via seaborn visualizes correlation matrix clearly.
- Sorting correlations with corr['Outcome'].sort_values() highlights features most correlated with the target.

corr = df.corr()
plt.figure(dpi=130)
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
plt.show()
print(corr['Outcome'].sort_values(ascending=False))

**Output: **

### Step 6: Visualize Target Variable Distribution

Check if target classes (Diabetes vs Not Diabetes) are balanced, affecting model training and evaluation.

- **plt.pie():**

plt.pie(clean_df['Outcome'].value_counts(),
        labels=['Diabetes', 'Not Diabetes'],
        autopct='%.f%%', shadow=True)
plt.title('Outcome Proportionality')       
plt.show()

**Output: **

### Step 7: Separate Features and Target Variable

Prepare independent variables (features) and dependent variable (target) separately for modeling.

- **df.drop(columns=[...]):**
- Direct column selection df['Outcome'] selects target column.

X = df.drop(columns=['Outcome'])
y = df['Outcome']

### Step 8: Feature Scaling: Normalization and Standardization

Scale features to a common range or distribution, important for many ML algorithms sensitive to feature magnitudes.

** 1. Normalization (Min-Max Scaling):** Rescales features between 0 and 1. Good for algorithms like k-NN and neural networks.

- **Class:**
- **.fit_transform():**

scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)
print(X_normalized[:5])

**Output: **

** 2. Standardization:** Transforms features to have mean = 0 and standard deviation = 1, useful for normally distributed features.

- **Class:**

scaler = StandardScaler()
X_standardized = scaler.fit_transform(X)
print(X_standardized[:5])

**Output:**

## Advantages

- Cleans and organizes raw data for better analysis.
- Removes noise and irrelevant data, leading to more precise predictions.
- Handles outliers and redundant features, which reduces overfitting.
- Scaling data helps models train faster by reducing computation time.
- Converts data into formats suitable for machine learning models.

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

- Source: [https://www.geeksforgeeks.org/data-analysis/data-preprocessing-machine-learning-python](https://www.geeksforgeeks.org/data-analysis/data-preprocessing-machine-learning-python)
