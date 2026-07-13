---
title: "Feature Engineering - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/machine-learning/what-is-feature-engineering"
library: "geeksforgeeks"
created: "2026-07-13T08:03:27.266827+00:00"
---

# Overview

Feature Engineering is the process of selecting, creating or modifying features like input variables or data to help machine learning models learn patterns more effectively. It involves transforming raw data into meaningful inputs that improve model accuracy and performance.

This step may include handling missing values, encoding categories, scaling numbers, creating new features or combining existing ones. It helps turn messy real-world data into a form that models can understand and use for better predictions.

### Importance of Feature Engineering

- **Improve accuracy**
- **Reduce overfitting**
- **Boost interpretability**
- **Enhance efficiency**

## Processes Involved in Feature Engineering

Lets see various features involved in feature engineering:

** 1. Feature Creation**: Feature creation involves generating new features from domain knowledge or by observing patterns in the data. It can be:

- **Domain-specific**
- **Data-driven**
- **Synthetic**

** 2. Feature Transformation**: Transformation adjusts features to improve model learning:

- **Normalization & Scaling**
- **Encoding**
- **Mathematical transformations**

** 3. Feature Extraction**: Transform existing features into a lower-dimensional or more informative representation (e.g., PCA).

- **Dimensionality reduction**
- **Aggregation & Combination**

** 4. Feature Selection**: Feature selection involves choosing a subset of relevant features to use:

- **Filter methods**
- **Wrapper methods**
- **Embedded methods**

** 5. Feature Scaling**: Scaling ensures that all features contribute equally to the model:

- **Min-Max scaling**
- **Standard scaling**

## Steps in Feature Engineering

Feature engineering can vary depending on the specific problem but the general steps are:

- **Data Cleaning:**
- **Data Transformation:**
- **Feature Extraction:**
- **Feature Selection:**
- **Feature Iteration:**

## Common Techniques in Feature Engineering

** 1. One-Hot Encoding**: One-Hot Encoding converts categorical variables into binary indicators, allowing them to be used by machine learning models.

import pandas as pd
data = {'Color': ['Red', 'Blue', 'Green', 'Blue']}
df = pd.DataFrame(data)
df_encoded = pd.get_dummies(df, columns=['Color'], prefix='Color')
print(df_encoded)

**Output**

Color_Blue Color_Green Color_Red 0 False False True 1 True False False 2 False True False 3 True False False

** 2. Binning**: Binning transforms continuous variables into discrete bins, making them categorical for easier analysis.

import pandas as pd
data = {'Age': [23, 45, 18, 34, 67, 50, 21]}
df = pd.DataFrame(data)
bins = [0, 20, 40, 60, 100]
labels = ['0-20', '21-40', '41-60', '61+']
df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
print(df)

**Output**

Age Age_Group 0 23 21-40 1 45 41-60 2 18 0-20 3 34 21-40 4 67 61+ 5 50 41-60 6 21 21-40

** 3. Text Data Preprocessing**: Involves removing stop-words, stemming and vectorizing text data to prepare it for machine learning models.

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
texts = ["This is a sample sentence.", "Text data preprocessing is important."]
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
vectorizer = CountVectorizer()
def preprocess_text(text):
    words = text.split()
    words = [stemmer.stem(word)
             for word in words if word.lower() not in stop_words]
    return " ".join(words)
cleaned_texts = [preprocess_text(text) for text in texts]
X = vectorizer.fit_transform(cleaned_texts)
print("Cleaned Texts:", cleaned_texts)
print("Vectorized Text:", X.toarray())

**Output:**

** 4. Feature Splitting**: Divides a single feature into multiple sub-features, uncovering valuable insights and improving model performance.

import pandas as pd
data = {'Full_Address': [
    '123 Elm St, Springfield, 12345', '456 Oak Rd, Shelbyville, 67890']}
df = pd.DataFrame(data)
df[['Street', 'City', 'Zipcode']] = df['Full_Address'].str.extract(
    r'([0-9]+\s[\w\s]+),\s([\w\s]+),\s(\d+)')
print(df)

**Output**

Full_Address Street City Zipcode 0 123 Elm St, Springfield, 12345 123 Elm St Springfield 12345 1 456 Oak Rd, Shelbyville, 67890 456 Oak Rd Shelbyville 67890...

## Tools for Feature Engineering

- **Featuretools**
- **TPOT**
- **DataRobot**
- **Alteryx**
- **H2O.ai:**

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

- Source: [https://www.geeksforgeeks.org/machine-learning/what-is-feature-engineering](https://www.geeksforgeeks.org/machine-learning/what-is-feature-engineering)
