---
title: "Introduction to Inferential Statistics - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/data-science/what-is-inferential-statistics"
library: "geeksforgeeks"
created: "2026-07-13T08:03:09.622134+00:00"
---

# Overview

Inferential statistics is an important tool that allows us to make predictions and conclusions about a population based on sample data. Unlike descriptive statistics, which only summarize data, inferential statistics let us test hypotheses, make estimates, and measure the uncertainty about our predictions.

These tools are essential for evaluating models, testing assumptions, and supporting data-driven decision-making.

For example

instead of surveying every voter in a country, we can survey a few thousand and still make reliable conclusions about the entire population’s opinion. Inferential statistics provides the tools to do this systematically and mathematically.,

**Need for Inferential Statistics**

**Need for Inferential Statistics**

In real-world scenarios, analyzing an entire population is often impossible. Instead, we collect data from a sample and use inferential statistics to:

- Conclude the whole population.
- Test claims or hypotheses.
- Calculate confidence intervals and p-values to measure uncertainty.
- Make predictions with statistical models.

## Techniques in Inferential Statistics

Inferential statistics offers several key methods for testing hypotheses, estimating population parameters, and making predictions. Here are the major techniques:

**1. **** Confidence Intervals:** It gives us a range of values that likely includes the true population parameter. It helps quantify the uncertainty of an estimate. The formula for calculating a confidence interval for the mean is:


\text{CI} = \bar{x} \pm Z_{\alpha/2} \times \frac{\sigma}{\sqrt{n}} 

Where:

- \bar{x} is the sample mean
- Z_{a/2}  is the Z-value from the standard normal distribution (e.g., 1.96 for a 95% confidence interval)
- \sigma is the population standard deviation
- n is the sample size

For example, if we measure the average height of 100 people, a 95% confidence interval gives us a range where the true population mean height is likely to fall. This helps gauge the precision of our estimate and compare models (like in A/B testing).

2. ** Hypothesis Testing**:

**Hypothesis testing is a formal procedure for testing claims or assumptions about data. It involves the following steps:**

- **Null Hypothesis (H₀)**
- **Alternative Hypothesis (H₁)**

We collect data and compute a test statistic (such as Z for a Z-test or t for a T-test):


Z = \frac{\bar{x} - \mu_0}{\frac{\sigma}{\sqrt{n}}} 

Where:

- \bar x is the sample mean
- \mu _0  is the hypothesized population mean
- \sigma is the population standard deviation
- n is the sample size

After calculating the test statistic, we compare it with a critical value or use a p-value to decide whether to reject or fail to accept the null hypothesis. If the p-value is smaller than the significance level α (usually 0.05), we reject the null hypothesis.


p\text{-value} = 2 \cdot P(Z > |z_{\text{obs}}|) 

Where 

3. ** Central Limit Theorem**: It states that the distribution of the sample mean will approximate a normal distribution as the sample size increases, regardless of the original population distribution. This is important because many statistical methods assume that data is normally distributed. The CLT can be mathematically expressed as:


\bar{X} \sim N\left(\mu, \frac{\sigma}{\sqrt{n}}\right) 

Where:

- \mu is the population mean
- \sigma is the population standard deviation
- n is the sample size

This theorem allows us to apply normal distribution-based methods even when the original data is not normally distributed, such as in cases with skewed income or shopping behavior data.

## Errors in Inferential Statistics

In hypothesis testing, Type I Error and Type II Error are key concepts:

- **Type I Error**- \alpha (the significance level).
- **Type II Error**- \beta and the power of the test is given by- 1-\beta .

The goal is to minimize these errors by carefully selecting sample sizes and significance levels.

## Parametric and Non-Parametric Tests

Statistical tests help decide if the data support a hypothesis. They calculate a test statistic that shows how much the data differs from the assumption (null hypothesis). This is compared to a critical value or p-value to accept or reject the null.

- **Parametric Tests:**
- **Non-Parametric Tests:**

## Example: Evaluating a New Delivery Algorithm Using Inferential Statistics

A quick commerce company wants to check if a new delivery algorithm reduces delivery times compared to the current system.

**Experiment Setup:**

- 100 orders split into two groups: 50 with the new algorithm, 50 with the current system.
- Delivery times for both groups are recorded.

**Steps**

**Steps**

**1. Hypotheses:**

- **Null (H0):**
- **Alternative (H1):**

**2. Significance Level:**

Set at 0.05 (5% risk of wrongly rejecting H0).

- **Type I error:**
- **Type II error:**

** 3. Test Statistic:** Compare average delivery times between the two groups

**4. Analysis:**

- Calculate means and differences.
- Check if the data is roughly normal.

**5. Perform a t-test or z-test: **

If p-value < 0.05, reject H0 and conclude the new algorithm is better. Otherwise, no clear improvement.

** 6. Confidence Interval: **For example, a range of -5 to -2 minutes means deliveries are 2 to 5 minutes faster with the new system.

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

- Source: [https://www.geeksforgeeks.org/data-science/what-is-inferential-statistics](https://www.geeksforgeeks.org/data-science/what-is-inferential-statistics)
