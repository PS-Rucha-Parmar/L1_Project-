---
title: "NumPy Tutorial - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/python/numpy-tutorial"
library: "geeksforgeeks"
created: "2026-07-13T07:55:24.543080+00:00"
---

# Overview

NumPy is a core Python library for numerical computing, built for handling large arrays and matrices efficiently. It is significantly faster than Python's built-in lists because it uses optimized C language style storage where actual values are stored at contiguous locations (not object reference).

- **ndarray object**
- **Vectorized operations**
- **Broadcasting**
- **Linear algebra functions**
- **Statistical functions**
- **Integration**

## Why Learn NumPy?

- Executes vectorized operations 10 to 100 times faster than standard Python loops.
- Uses homogeneous arrays to store large datasets more compactly than Python lists.
- Provides optimized functions for linear algebra, Fourier transforms and matrix manipulations.
- Includes robust tools for statistics, random number generation and missing data management.
- Expresses complex math in single-line commands, eliminating the need for manual, nested loops.

## Basics

This section covers NumPy installation, importing, core features and its advantages over Python lists for numerical computing.

## NumPy Arrays

NumPy arrays (ndarrays) are the backbone of the library. This section covers how to create and manipulate arrays effectively for data storage and processing

import numpy as np
a = [9,3,3,5]
print(np.array(a))  # Converting list into numpy array

**Output**

[9 3 3 5]

- Basics
- Creating NumPy Arrays
- Numpy Array Indexing & Slicing
- Reshaping & Resizing Arrays
- Stacking & Splitting Arrays
- Broadcasting

## Mathematical Operations

This section covers essential mathematical functions for array computations, including basic arithmetic, aggregation and mathematical transformations.

import numpy as np
n = np.array([9,3,3,5])
print(n.mean())    # Calculating mean

**Output**

5.0

- Basic Arithmetic Operations
- Aggregation Functions: sum, mean, max, min
- Universal Functions
- Mathematical Functions

## Linear Algebra

NumPy provides built-in functions for linear algebra operations essential for scientific computing and machine learning applications.

import numpy as np
A = np.array([[1, 2],
              [3, 4]])
res = np.dot(A, A)    # Matrix multiplication
print(res) 

**Output**

[[ 7 10] [15 22]]

- Matrix Multiplication & Manipulation
- Matrix & vector products
- Determinants & Inverse of a Matrix
- Inner & Outer Functions
- Dot and Vdot Functions
- Eigenvalues and Eigenvectors

## Random Number Generation and Statistics

NumPy’s random module provides a list of functions for generating random numbers, which are essential for simulations, cryptography and machine learning applications.

import numpy as np
a = np.random.normal(0, 1, 5)    # 5 values from normal distribution
print("Data:", a)
print("Mean:", np.mean(a))

**Output**

Data: [ 0.50380896 1.56391917 -0.25398057 -0.31520396 0.4174568 ] Mean: 0.38320007938038125

- Generating Random Numbers
- Normal Distribution
- Binomial Distribution
- Poisson Distribution
- Uniform Distribution
- Exponential Distribution
- Chi-square Distribution
- Statistical Functions (mean, median, variance, standard deviation)

## Advanced Operations

This section includes vectorized operations for speed optimization, memory management strategies and integration with Pandas for efficient data analysis.

import numpy as np
a = np.arange(5)
r = a * 10    # Vectorized operation (fast and efficient)
print(r)

**Output**

[ 0 10 20 30 40]

## Quiz & Practice

Test your knowledge of NumPy with this quiz, covering key topics such as array operations, mathematical functions and broadcasting.

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

- Source: [https://www.geeksforgeeks.org/python/numpy-tutorial](https://www.geeksforgeeks.org/python/numpy-tutorial)
