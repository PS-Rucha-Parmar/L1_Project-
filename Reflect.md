# Reflect.md

# L1 Reflection – Building with Large Language Models

## Overview

This course gave me a practical introduction to Large Language Models (LLMs) and the technologies used to build AI-powered applications. Before starting the course, I had used AI tools but didn't fully understand how they worked internally or how developers build applications around them.

By the end of this course, I gained an understanding of the complete workflow behind modern AI applications—from prompting an LLM to building Retrieval-Augmented Generation (RAG) systems and connecting AI with external tools using the Model Context Protocol (MCP).

---

# What I Learned

## 1. Understanding Generative AI

I learned that Generative AI is a branch of Artificial Intelligence capable of generating new content such as text, images, code, audio, and more instead of simply classifying existing data.

I also understood the relationship between:

- Artificial Intelligence (AI)
- Machine Learning (ML)
- Deep Learning (DL)
- Large Language Models (LLMs)
- Generative AI

This helped me see where LLMs fit within the broader AI ecosystem.

---

## 2. How Large Language Models Work

One of the most valuable parts of the course was learning how an LLM actually works.

I learned about:

- Tokens
- Tokenization
- Context Windows
- Prompt Processing
- Transformer architecture (high level)
- Probability-based next token prediction

Instead of "thinking" like humans, LLMs predict the most probable next token based on the previous context.

Understanding this completely changed how I think about AI responses.

---

## 3. Prompt Engineering

I learned that the quality of an AI response depends heavily on the quality of the prompt.

Important concepts included:

- System Prompt
- User Prompt
- Context
- Guardrails
- Clear instructions
- Role assignment
- Output formatting

I also learned why system prompts have higher priority than user prompts and how prompt design affects reliability.

---

## 4. LLM Parameters

The course introduced several important parameters used while interacting with LLMs.

These included:

- Temperature
- Top-P
- Maximum Tokens
- Context Window

I understood how these parameters influence creativity, determinism, response length, and model behavior.

---

## 5. Retrieval-Augmented Generation (RAG)

This was one of the most useful sections because it explained how developers provide external knowledge to an LLM.

I learned the complete RAG pipeline:

```
Documents
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector Database
      ↓
Similarity Search
      ↓
Retrieved Context
      ↓
Large Language Model
      ↓
Grounded Response
```

Instead of training the model again, RAG retrieves relevant information during inference.

This makes responses:

- More accurate
- More up-to-date
- Easier to maintain
- Less prone to hallucinations

---

## 6. Vector Databases

Before this course I had heard of vector databases but didn't know why they were necessary.

I learned:

- What embeddings are
- Semantic search
- Similarity search
- Cosine similarity
- Vector indexing
- Why traditional SQL databases are not suitable for semantic retrieval

I also learned that vector databases store embeddings instead of raw text, allowing the system to search by meaning instead of exact keywords.

---

## 7. Choosing Between Prompting, RAG and Fine-Tuning

One of the biggest takeaways was understanding when to use each approach.

### Prompting

Use when:

- General knowledge is sufficient
- No external data is required

---

### RAG

Use when:

- Information changes frequently
- Company documents are involved
- Responses should include citations
- Knowledge should remain separate from the model

---

### Fine-Tuning

Use when:

- Teaching a specific writing style
- Learning specialized behavior
- Repeated task optimization

I learned that many real-world business applications can be solved with RAG instead of expensive fine-tuning.

---

## 8. Model Context Protocol (MCP)

The introduction to MCP helped me understand how AI systems communicate with external tools.

Instead of directly integrating every API into the LLM, MCP provides a standardized way for AI assistants to interact with different applications.

This allows AI systems to access tools while keeping the architecture modular and scalable.

---

# Hands-on Experience

The course also included a practical MCP exercise.

As part of the activity, I successfully connected:

- Atlassian
- Antigravity

using the **Model Context Protocol (MCP)**.

This demonstrated how an LLM can communicate with external services through standardized tool connections instead of relying only on its built-in knowledge.

This practical exercise helped reinforce the concepts introduced during the lessons.

---

# Key Terms I Learned

Some of the important concepts introduced during the course include:

- Artificial Intelligence (AI)
- Machine Learning (ML)
- Deep Learning
- Generative AI
- Large Language Models (LLMs)
- Tokens
- Context Window
- Prompt Engineering
- System Prompt
- User Prompt
- Embeddings
- Chunking
- Vector Database
- Semantic Search
- Similarity Search
- Retrieval-Augmented Generation (RAG)
- Fine-Tuning
- MCP (Model Context Protocol)

---

# Biggest Takeaways

The biggest lesson from this course was realizing that building AI applications involves much more than simply calling an LLM.

A production-ready AI assistant typically requires:

- Well-designed prompts
- Reliable context retrieval
- Vector search
- External knowledge sources
- Tool integration
- Proper architecture choices

Understanding these building blocks has given me a much clearer picture of how modern AI systems are designed.

---

# Skills Gained

After completing this course, I am able to:

- Explain how Large Language Models generate responses.
- Understand tokenization and context windows.
- Write more effective prompts.
- Explain how Retrieval-Augmented Generation works.
- Describe why vector databases are used in semantic search.
- Differentiate between Prompting, RAG, and Fine-Tuning.
- Understand the purpose of MCP for tool integration.
- Build a basic RAG workflow conceptually.
- Connect external services using MCP.

---

# Personal Reflection

This course transformed my understanding of AI from simply using language models to understanding how they are built into real-world applications.

The concepts covered in this course have provided a strong foundation for future work involving Retrieval-Augmented Generation, AI agents, vector databases, and tool integrations.

I now feel much more confident exploring larger AI projects and understanding the architectural decisions involved in building intelligent applications.
