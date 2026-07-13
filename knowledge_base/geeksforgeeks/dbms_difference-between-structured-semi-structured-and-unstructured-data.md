---
title: "Difference between Structured, Semi-structured and Unstructured data - GeeksforGeeks"
url: "https://www.geeksforgeeks.org/dbms/difference-between-structured-semi-structured-and-unstructured-data"
library: "geeksforgeeks"
created: "2026-07-13T07:59:33.958433+00:00"
---

# Overview

**Big Data** includes huge volume, high velocity, and extensible variety of data. There are 3 types: Structured data, Semi-structured data, and Unstructured data. 

 

- **Structured data -**
 Structured data is data whose elements are addressable for effective analysis. It has been organized into a formatted repository that is typically a database. It concerns all data which can be stored in database SQL in a table with rows and columns. They have relational keys and can easily be mapped into pre-designed fields. Today, those data are most processed in the development and simplest way to manage information.- *Example:*Relational data.
 
- **Semi-Structured data -**
 Semi-structured data is information that does not reside in a relational database but that has some organizational properties that make it easier to analyze. With some processes, you can store them in the relation database (it could be very hard for some kind of semi-structured data), but Semi-structured exist to ease space.- *Example*: XML data.
 
- **Unstructured data -**
 Unstructured data is a data which is not organized in a predefined manner or does not have a predefined data model, thus it is not a good fit for a mainstream relational database. So for Unstructured data, there are alternative platforms for storing and managing, it is increasingly prevalent in IT systems and is used by organizations in a variety of business intelligence and analytics applications.- *Example*: Word, PDF, Text, Media logs.
 

**Differences between Structured, Semi-structured and Unstructured data:** 

| Properties | Structured data | Semi-structured data | Unstructured data | 
|---|---|---|---|
| Technology | It is based on Relational database table | It is based on XML/RDF(Resource Description Framework). | It is based on character and binary data | 
| Transaction management | Matured transaction and various concurrency techniques | Transaction is adapted from DBMS not matured | No transaction management and no concurrency | 
| Version management | Versioning over tuples,row,tables | Versioning over tuples or graph is possible | Versioned as a whole | 
| Flexibility | It is schema dependent and less flexible | It is more flexible than structured data but less flexible than unstructured data | It is more flexible and there is absence of schema | 
| Scalability | It is very difficult to scale DB schema | It's scaling is simpler than structured data | It is more scalable. | 
| Robustness | Very robust | New technology, not very spread | -- | 
| Query performance | Structured query allow complex joining | Queries over anonymous nodes are possible | Only textual queries are possible |

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

- Source: [https://www.geeksforgeeks.org/dbms/difference-between-structured-semi-structured-and-unstructured-data](https://www.geeksforgeeks.org/dbms/difference-between-structured-semi-structured-and-unstructured-data)
