---
title: "Statistics For Data Science - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/data-science/statistics-for-data-science"
library: "geeksforgeeks"
created: "2026-07-13T07:53:19.686175+00:00"
---

# Overview

Statistics is the science of collecting, analyzing, and interpreting data to uncover patterns and make decisions. In data science, it acts as the backbone for understanding data and building reliable models.

- Summarizes data using measures like mean, median, and variance
- Models uncertainty with probability and distributions
- Tests hypotheses (e.g., A/B testing)
- Finds relationships through regression and correlation

## Types of Statistics

There are commonly two types of statistics, which are discussed below:

- **Descriptive Statistics:**
- **Inferential Statistics:**

## What is Data in Statistics?

Data is a collection of observations, it can be in the form of numbers, words, measurements, or statements.

### Types of Data

**1. **** Qualitative Data:** This data is descriptive. For example - She is beautiful, He is tall, etc.

** 2. Quantitative Data: **This is numerical information. For example - A horse has four legs.

- **Discrete Data:**
- **Continuous Data:**

## Basics of Statistics

Basic formulas of statistics are,

| Parameters | Definition | Formulas | 
|---|---|---|
| Population Mean (μ)  | Average of the entire group. | |
| Sample Mean | Average of a subset of the population | |
| Sample/Population Standard Deviation | Measures how spread out the data is from the mean | |
| Sample/Population Variance | Shows how far values are from the mean, squared | |
| Class Interval(CI) | Range of values in a group | CI = Upper Limit − Lower Limit | 
| Frequency(f) | How often a value appears | Count of occurrences | 
| Range (R) | Difference between largest and smallest values | Range = Max−Min | 

## Measure of Central Tendency

** 1. Mean**: The mean can be calculated by summing all values present in the sample divided by total number of values present in the sample or population.


Formula:Mean (\mu) = \frac{Sum \, of \, Values}{Number \, of \, Values} 

** 2. Median: **The median is the middle of a dataset when arranged from lowest to highest or highest to lowest in order to find the median, the data must be sorted. For an odd number of data points the median is the middle value and for an even number of data points median is the average of the two middle values.

** 3. Mode: **The most frequently occurring value in the Sample or Population is called as Mode.

## Measure of Dispersion

- **Range:**
- **Variance (σ²):**


Formula:\sigma^2~=~\frac{\Sigma(X-\mu)^2}{n} 

- **Standard Deviation (σ):**


Formula:\sigma=\sqrt(\sigma^2)=\sqrt(\frac{\Sigma(X-\mu)^2}{n}) 

- **Interquartile Range (IQR):**

Formula: IQR = Q_3 -Q_1 

- **Quartiles**

Q1 (First Quartile): Median of the lower 50% of the dataset (25th percentile).

Q2 (Second Quartile / Median): Median of the entire dataset (50th percentile).

Q3 (Third Quartile): Median of the upper 50% of the dataset (75th percentile).


- **Mean Absolute Deviation:**


Formula: Mean \, Absolute \, Deviation = \frac{\sum_{i=1}^{n}{|X - \mu|}}{n} 

- **Coefficient of Variation (CV):**
 CV is the ratio of the standard deviation to the mean, expressed as a percentage. It is useful for comparing the relative variability of different datasets.


CV = (\frac{\sigma}{\mu}) * 100 

## Measure of Shape

### 1. Skewness

Skewness is the measure of asymmetry of probability distribution about its mean.

**Types of Skewed data**

- **Positive Skew (Right):**
- **Negative Skew (Left):**
- **Symmetrical:**

### 2. Kurtosis

Kurtosis quantifies the degree to which a probability distribution deviates from the normal distribution. It assesses the "tailedness" of the distribution, indicating whether it has heavier or lighter tails than a normal distribution. High kurtosis implies more extreme values in the distribution, while low kurtosis indicates a flatter distribution.

#### Types of Kurtosis

- **Mesokurtic:**
- **Leptokurtic:**
- **Platykurtic:**

## Measure of Relationship

- **Covariance**


Cov(x,y) = \frac{\sum(X_i-\overline{X})(Y_i - \overline{Y})}{n} 

- **Correlation**


\rho(X, Y) = \frac{cov(X,Y)}{\sigma_X \sigma_Y} 

## Probability Theory

Here are some basic concepts or terminologies used in probability:

| Term | Definition | 
|---|---|
| Sample Space | The set of all possible outcomes in a probability experiment. | 
| Event | A subset of the sample space. | 
| Joint Probability (Intersection of Event) | Probability of occurring events A and B. Formula: P(A and B) = P(A) × P(B) | 
| Union of Events | Probability of occurring events A or B. Formula: P(A or B) = P(A) + P(B) - P(A and B) | 
| Conditional Probability | Probability of occurring events A when event B has occurred. Formula: P(A | B) = P(A and B)/P(B) | 

### Bayes Theorem

Bayes' Theorem is a fundamental concept in probability theory that relates conditional probabilities. It is named after the Reverend Thomas Bayes, who first introduced the theorem. Bayes' Theorem is a mathematical formula that provides a way to update probabilities based on new evidence. The formula is as follows:


P(A|B) = \frac{P(B|A) \times P(A)}{P(B)} 

where

- *P*- *A*- *B*
- *P*- *B*- *A*

### Types of Probability Functions

- **Probability Mass Function(PMF)**
- **Probability Density Function (PDF)**
- **Cumulative Distribution Function (CDF)**
- **Empirical Distribution Function (EDF):**

## Probability Distributions Functions

### 1. Normal or Gaussian Distribution

The normal distribution is a continuous probability distribution characterized by its bell-shaped curve and can be by described by mean (μ) and standard deviation (σ).


Formula:f(X|\mu,\sigma)=\frac{\epsilon^{-0.5(\frac{X-\mu}{\sigma})^2}}{\sigma\sqrt(2\pi)} 

** Empirical Rule (68-95-99.7 Rule): **~68% data within 1σ, ~95% within 2σ, ~99.7% within 3σ.

** Use: **Detecting outliers, modeling natural phenomena.


Central Limit Theorem (CLT) states that, regardless of the shape of the original population distribution, the sampling distribution of the sample mean will be approximately normally distributed if the sample size tends to infinity.Central Limit Theorem: The

### 2. Student t-distribution

The t-distribution, also known as Student's t-distribution, is a probability distribution that is used in statistics.


f(t) =\frac{\Gamma\left(\frac{df+1}{2}\right)}{\sqrt{df\pi} \, \Gamma\left(\frac{df}{2}\right)} \left(1 + \frac{t^2}{df}\right)^{-\frac{df+1}{2}} 

- **Parameter:**
- **Use:**

### 3. Chi-square Distribution

The chi-squared distribution, denoted as 


\chi^2 = \frac 1{2^{k/2}\Gamma {(k/2)}} x^{{\frac k 2}-1} e^{\frac {-x}2} 

### 4. Binomial Distribution

The binomial distribution models the number of successes in a fixed number of independent Bernoulli trials, where each trial has the same probability of success (* p*).


Formula:P(X=k)=(^n_k)p^k(1-p)^{n-k} 

### 5. Poisson Distribution

The poisson distribution models the number of events that occur in a fixed interval of time or space. It's characterized by a single parameter (* λ*), the average rate of occurrence.


Formula:P(X=k)=\frac{\epsilon^{-\lambda}\lambda^k}{k!} 

### 6. Uniform Distribution

The uniform distribution represents a constant probability for all outcomes in a given range.

Formula:

f(X)=\frac{1}{b-a} 

## Parameter estimation for Statistical Inference

- **Population:**
- **Sample:**
- **Expectation (E[x]):**
- **Parameter:**
- **Statistic:**
- **Estimation:**
- **Estimator:**
- **Bias:**


Bias(\widehat{\theta}) = E(\widehat{\theta}) - \theta 

## Hypothesis Testing

Hypothesis testing makes inferences about a population parameter based on sample statistic.

** 1. Null Hypothesis (H₀): ** There is no significant difference or effect.

** 2. Alternative Hypothesis (H₁): **There is a significant effect i.e the given statement can be false. 

** 3. Degrees of freedom**: Degrees of freedom (df) in statistics represent the number of values or quantities in the final calculation of a statistic that are free to vary. It is mainly defined as sample size-one (n-1).

**4. Level of Significance(**** )**: This is the threshold used to determine statistical significance. Common values are 0.05, 0.01, or 0.10.

** 5. p-value: **The p-value probability of observing results if H₀ is true.

- If p ≤ α: reject H₀
- If p > α: fail to reject H₀

**6. Type I Error and Type II Error**

- Type I Error that occurs when the null hypothesis is true, but the statistical test incorrectly rejects it. It is often referred to as a "false positive" or "alpha error."
- Type II Error that occurs when the null hypothesis is false, but the statistical test fails to reject it. It is often referred to as a "false negative."

** 7. Confidence Intervals**: A confidence interval is a range of values that is used to estimate the true value of a population parameter with a certain level of confidence. It provides a measure of the uncertainty or margin of error associated with a sample statistic, such as the sample mean or proportion.

**Example of Hypothesis **

**Example of Hypothesis**

An e-commerce company wants to know if a website redesign affects average user session time.


Mean = 3.5 min, SD = 1.2, n = 50Before:
Mean = 4.2 min, SD = 1.5, n = 60After:

Hypotheses:

- H₀: No change (μ_after − μ_before = 0)
- H₁: Positive change (μ_after − μ_before > 0)

α = 0.05Significance Level:Difference in means -> calculate p-valueTest:

Interpretation:

- If p < 0.05: Redesign significantly increased session time
- If p ≥ 0.05: No significant effect

## Statistical Tests

Parametric test are statistical methods that make assumption that the data follows normal distribution.

| Z-test | t-test | F-test | 
|---|---|---|
| Tests if a sample mean differs from a known population mean. | Compares means when population standard deviation is unknown. | Compares variances of two or more groups. | 
| Population standard deviation is known and sample size is large. | Small samples or unknown population standard deviation. | To test if group variances are significantly different. | 
| One-Sample Test: Z = Two-Sample Test: Z =  | One- sample: t =  Two-Sample Test: Paired t-Test: t= |  | 

### ANOVA (Analysis Of Variance)

| Source of Variation | Sum of Squares | Degrees Of Freedom | Mean Squares | F-Value | 
|---|---|---|---|---|
| Between Groups | SSB=  | df | MSB= SSB/ (k-1) | f=MSB/MSE | 
| Error | SSE= | df | MSE=SSE/(N-k) | |
| Total | SST= SSB+SSE | df | 

There are mainly ** two types **of ANOVA:

1. One-way ANOVA: Compares means of 3+ groups.

- **H₀:**
- **H₁:**

2. Two-way ANOVA: Tests impact of two categorical variables and their interaction

### Chi-Squared Test

The chi-squared test is a statistical test used to determine if there is a significant association between two categorical variables. It compares the observed frequencies in a contingency table with the frequencies.


Formula:X^2=\Sigma{\frac{(O_{ij}-E_{ij})^2}{E_{ij}}} 

This test is also performed on big data with multiple number of observations.

## Non-Parametric Test

Non-parametric test does not make assumptions about the distribution of the data. They are useful when data does not meet the assumptions required for parametric tests.

- **Mann-Whitney U Test:**- **t-test are not met.**
- **Kruskal-Wallis Test:**

## A/B Testing or Split Testing

A/B testing, also known as split testing, is a method used to compare two versions (A and B) of a webpage, app, or marketing asset to determine which one performs better.

** Example: **a product manager change a website's "Shop Now" button color from green to blue to improve the click-through rate (CTR). Formulating null and alternative hypotheses, users are divided into A and B groups and CTRs are recorded. Statistical tests like chi-square or t-test are applied with a 5% confidence interval. If the p-value is below 5%, the manager may conclude that changing the button color significantly affects CTR, informing decisions for permanent implementation.

## Regression

Regression is a statistical technique used to model the relationship between a dependent variable and one or more independent variables.

The equation for regression:

y=\alpha+ \beta x 

Where,

- *y*
- *x*
- \alpha is the intercept
- \beta is the regression coefficient.

Regression coefficient is a measure of the strength and direction of the relationship between a predictor variable (independent variable) and the response variable (dependent variable)

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

- Source: [https://www.geeksforgeeks.org/data-science/statistics-for-data-science](https://www.geeksforgeeks.org/data-science/statistics-for-data-science)
