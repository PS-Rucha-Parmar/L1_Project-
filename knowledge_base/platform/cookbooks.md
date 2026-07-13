---
title: "Claude Cookbook"
url: "https://platform.claude.com/cookbooks"
library: "platform"
created: "2026-07-13T07:53:28.037096+00:00"
---

# Overview

| Reproduce Claude's agentic search benchmark scores in the Messages API Build a Messages API harness that reproduces published DeepSearchQA and BrowseComp scores, using programmatic tool calling, server-side compaction, and task budgets. | EvalsTools | Mengting Li | Jun 2026 | 
| Classifier fallback and billing for Claude Fable 5 Jun 2026•ResponsesSafeguardsBilling Detect safety classifier blocks on Fable 5 and fall back to Opus 4.8 with server-side or SDK-based client-side fallback, including streaming behavior and the new billing changes. | ResponsesSafeguardsBilling | Alexander Bricken Mahesh Murag Mikaela Grace | Jun 2026 | 
| Async multi-agent orchestration Two async multi-agent patterns — a fixed N-agent team with peer messaging through a shared hub, and dynamically spawned async subagents — reduced to their bare messaging and lifecycle mechanics. | Agent Patterns | Paul Chen | Jun 2026 | 
| Hosting your agent May 2026•Claude Agent SDK Deploy the research agent from notebook 00 through three tiers of operational maturity (Docker, Modal, Kubernetes) with the same container image and HTTP interface at every tier. | Claude Agent SDK | Kevin Tang Anav Sharma | May 2026 | 
| Multiagent: coordinate a specialist team May 2026•Claude Managed AgentsTools Heterogeneous team via the multiagent coordinator config — a coordinator runs three specialists (web-search researcher, file-reading librarian, rules-based pricer) with scoped toolsets to assemble a sales proposal. Covers the multiagent field, the thread_created / thread_message_received event types, and per-role tool scoping. | Claude Managed AgentsTools | Mark Nowicki | May 2026 | 
| Outcomes: agents that verify their own work May 2026•Claude Managed AgentsEvals Build a grade-and-revise loop with Outcomes: a writer drafts a cited research brief, a stateless grader fetches every URL and checks every quote against a rubric, and feedback drives revisions until the brief passes. Covers user.define_outcome, the span.outcome_evaluation_* events, and how to write a rubric the grader can act on. | Claude Managed AgentsEvals | Mark Nowicki Gagan Bhat | May 2026 | 
| Build agents that remember your users Apr 2026•Claude Managed AgentsTools Give your Claude Managed Agents a Memory store so they learn and remember your users' preferences across multiple interactions. | Claude Managed AgentsTools | Gagan Bhat | Apr 2026 | 
| The vulnerability detection agent Apr 2026•Claude Agent SDKCybersecurity Build a vulnerability-discovery agent with the Claude Agent SDK that threat-models a C target, hunts memory-safety bugs with built-in file tools, and triages findings into a structured report. | Claude Agent SDKCybersecurity | Eugene Yan | Apr 2026 | 
| Build an SRE incident response agent with Claude Managed Agents Apr 2026•Claude Managed AgentsObservability Wire Claude into your on-call flow: when an alert fires, the agent reads logs and runbooks, pinpoints the root cause, opens a fix PR, and waits for your approval before merging. | Claude Managed AgentsObservability | Gagan Bhat | Apr 2026 | 
| Build a data analyst agent with Claude Managed Agents Apr 2026•Claude Managed AgentsTools Build an analyst that turns a CSV into a narrative HTML report with interactive charts, using a sandboxed environment and file mounting. | Claude Managed AgentsTools | Charmaine Lee Jess Yan | Apr 2026 | 
| Build a Slack data analyst bot with Claude Managed Agents Apr 2026•Claude Managed AgentsIntegrations Mention the bot with a CSV to get an analysis report in-thread, with multi-turn follow-ups on the same session. | Claude Managed AgentsIntegrations | Charmaine Lee | Apr 2026 | 
| Managed Agents tutorial: iterate on a failing test suite Apr 2026•Claude Managed AgentsTools Entry-point tutorial for the Claude Managed Agents API. Walks through agent / environment / session creation, file mounts, and the streaming event loop by getting an agent to fix three planted bugs in a calc.py package. | Claude Managed AgentsTools | Paul Yang | Apr 2026 | 
| Managed Agents tutorial: production setup Apr 2026•Claude Managed AgentsIntegrations End-to-end production story for Managed Agents — vault-backed MCP credentials, the session.status_idled webhook pattern for human-in-the-loop without long-lived connections, and the resource lifecycle CRUD verbs. | Claude Managed AgentsIntegrations | Paul Yang | Apr 2026 | 
| Managed Agents tutorial: prompt versioning and rollback Apr 2026•Claude Managed AgentsEvals Server-side prompt versioning — create v1, evaluate against a labelled test set, ship v2, detect a regression, roll back by pinning sessions to version 1. Covers agents.update, version pinning on sessions.create, and where the review gate moves when prompts are not code. | Claude Managed AgentsEvals | Mark Nowicki | Apr 2026 | 
| Threat intelligence enrichment agent Apr 2026•ToolsAgent PatternsCybersecurity Build an agent that autonomously investigates IOCs by querying multiple threat intel sources, cross-referencing findings, mapping to MITRE ATT&CK, and producing structured reports for SIEM and SOAR integration. | ToolsAgent PatternsCybersecurity | Jannet Park | Apr 2026 | 
| Building a session browser Mar 2026•Claude Agent SDKAgent Patterns List, read, rename, tag, and fork Agent SDK sessions on disk to build a conversation history sidebar without writing a transcript parser. | Claude Agent SDKAgent Patterns | Qing Wang | Mar 2026 | 
| Knowledge graph construction with Claude Mar 2026•RAG & RetrievalTools Build knowledge graphs from unstructured text using Claude for entity extraction, relation mining, deduplication, and multi-hop graph querying. | RAG & RetrievalTools | Anthropic | Mar 2026 | 
| Context engineering: memory, compaction, and tool clearing Mar 2026•ToolsAgent Patterns Compare context engineering strategies for long-running agents and learn when each applies, what it costs, and how they compose. | ToolsAgent Patterns | Isabella He | Mar 2026 | 
| Migrating from the OpenAI Agents SDK Mar 2026•Claude Agent SDKAgent Patterns Port an OpenAI Agents SDK app to the Claude Agent SDK, mapping each primitive (tools, guardrails, sessions, handoffs) through a single expense-approval agent example. | Claude Agent SDKAgent Patterns | Preston Tuggle | Mar 2026 | 
| The site reliability agent Feb 2026•Claude Agent SDKAgent Patterns Build an incident response agent with read-write MCP tools for autonomous diagnosis, remediation, and post-mortem documentation. | Claude Agent SDKAgent Patterns | Ben Lehrburger Isabella He | Feb 2026 | 
| Session memory compaction Jan 2026•Agent PatternsResponses Manage long-running Claude conversations with instant session memory compaction using background threading and prompt caching. | Agent PatternsResponses | Joe Shamon | Jan 2026 | 
| Programmatic tool calling (PTC) Reduce latency and token consumption by letting Claude write code that calls tools programmatically in the code execution environment. | Tools | Pedram Navid | Nov 2025 | 
| Tool search with embeddings Nov 2025•ToolsRAG & Retrieval Scale Claude applications to thousands of tools using semantic embeddings for dynamic tool discovery. | ToolsRAG & Retrieval | Henry Keetay | Nov 2025 | 
| Automatic context compaction Nov 2025•ToolsAgent Patterns Manage context limits in long-running agentic workflows by automatically compressing conversation history. | ToolsAgent Patterns | Pedram Navid | Nov 2025 | 
| Low latency voice assistant with ElevenLabs Build a low-latency voice assistant using ElevenLabs for speech-to-text and text-to-speech combined with Claude. | Integrations | Adriaan Engelbrecht | Nov 2025 | 
| Giving Claude a crop tool for better image analysis Give Claude a crop tool to zoom into image regions for detailed analysis of charts, documents, and diagrams. | MultimodalTools | Nadine Yasser | Nov 2025 | 
| Prompting for frontend aesthetics Guide to prompting Claude for distinctive, polished frontend designs avoiding generic aesthetics. | ResponsesSkills | Prithvi Rajasekaran | Oct 2025 | 
| Claude Skills for financial applications Build financial dashboards and portfolio analytics using Claude's Excel, PowerPoint, PDF skills. | Skills | Alex Notov | Oct 2025 | 
| Building custom Skills for Claude Create, deploy, and manage custom skills extending Claude with specialized organizational workflows. | Skills | Alex Notov | Oct 2025 | 
| Introduction to Claude Skills Create documents, analyze data, automate workflows with Claude's Excel, PowerPoint, PDF skills. | Skills | Alex Notov | Oct 2025 | 
| The one-liner research agent Sep 2025•Claude Agent SDKAgent Patterns Build a research agent using Claude Code SDK with WebSearch for autonomous research. | Claude Agent SDKAgent Patterns | Rodrigo Olivares Jiri De Jonghe | Sep 2025 | 
| The chief of staff agent Sep 2025•Claude Agent SDKAgent Patterns Build multi-agent systems with subagents, hooks, output styles, and plan mode features. | Claude Agent SDKAgent Patterns | Rodrigo Olivares Jiri De Jonghe | Sep 2025 | 
| The observability agent Sep 2025•Claude Agent SDKAgent Patterns Connect agents to external systems via MCP servers for GitHub monitoring and CI workflows. | Claude Agent SDKAgent Patterns | Rodrigo Olivares Jiri De Jonghe | Sep 2025 | 
| Tool evaluation Run parallel agent evaluations on tools independently from evaluation task files. | Evals | Anthropic | Sep 2025 | 
| Usage & cost Admin API cookbook Programmatically access and analyze your Claude API usage and cost data via Admin API. | Observability | Anthropic | Aug 2025 | 
| Memory & context management with Claude Sonnet 4.6 May 2025•ToolsAgent Patterns Build AI agents with persistent memory using Claude's memory tool and context editing. | ToolsAgent Patterns | Alex Notov | May 2025 | 
| Speculative prompt caching Reduce time-to-first-token by warming cache speculatively while users formulate their queries. | Responses | Anthropic | May 2025 | 
| Parallel tool calls on Claude 3.7 Sonnet Enable parallel tool calls on Claude 3.7 Sonnet using batch tool meta-pattern workaround. | Tools | Anthropic | Mar 2025 | 
| Extended thinking Use Claude's extended thinking for transparent step-by-step reasoning with budget management. | Thinking | Alex Albert | Feb 2025 | 
| Extended thinking with tool use Combine extended thinking with tools for transparent reasoning during multi-step workflows. | ThinkingTools | Alex Albert | Feb 2025 | 
| Basic workflows Three simple multi-LLM workflow patterns trading cost or latency for improved performance. | Agent Patterns | Anthropic | Dec 2024 | 
| Evaluator optimizer Dec 2024•Agent PatternsEvals Workflow pattern using one LLM for generation and another for evaluation feedback loop. | Agent PatternsEvals | Anthropic | Dec 2024 | 
| Orchestrator workers Central LLM dynamically delegates tasks to worker LLMs and synthesizes their combined results. | Agent Patterns | Anthropic | Dec 2024 | 
| Batch processing with Message Batches API Process large volumes of Claude requests asynchronously with 50% cost reduction using batches. | Responses | Alex Albert | Oct 2024 | 
| Text to SQL with Claude Convert natural language queries to SQL using RAG, chain-of-thought, and self-improvement techniques. | RAG & Retrieval | Mahesh Murag | Sep 2024 | 
| Enhancing RAG with contextual retrieval Improve RAG accuracy by adding context to chunks before embedding with prompt caching. | RAG & Retrieval | Anthropic | Sep 2024 | 
| Finetuning Claude 3 Haiku on Bedrock Step-by-step guide to finetuning Claude 3 Haiku on Amazon Bedrock for custom tasks. | Fine-Tuning | David Hershey | Aug 2024 | 
| Generate synthetic test data for your prompt template Generate synthetic test cases to evaluate and improve your Claude prompt templates effectively. | Evals | Anthropic | Aug 2024 | 
| Prompt caching through the Claude API Cache and reuse prompt context for cost savings and faster responses with detailed instructions. | Responses | Alex Albert | Aug 2024 | 
| Summarization with Claude Aug 2024•RAG & RetrievalResponses Comprehensive guide to summarizing legal documents with evaluation and advanced techniques. | RAG & RetrievalResponses | Alexander Bricken | Aug 2024 | 
| Retrieval augmented generation Build and optimize RAG systems with Claude using summary indexing and reranking techniques. | RAG & Retrieval | Anthropic | Jul 2024 | 
| Classification with Claude Build classification systems with Claude using RAG and chain-of-thought for insurance tickets. | RAG & Retrieval | Garvan Doyle | May 2024 | 
| Tool choice Control how Claude selects tools using tool_choice parameter for forced or auto selection. | Tools | Alex Albert | May 2024 | 
| Using vision with tools Combine Claude's vision with tools to extract structured data from images like nutrition labels. | MultimodalTools | Alex Albert | May 2024 | 
| Sampling responses from Claude beyond the max tokens limit Generate longer responses beyond max_tokens limit using prefill technique with message continuation. | Responses | Anthropic | May 2024 | 
| Best practices for using vision with Claude Tips and techniques for optimal image processing performance with Claude's vision capabilities. | Multimodal | Alex Albert | May 2024 | 
| Note-saving tool with Pydantic and Anthropic tool use Create validated tools using Pydantic models for type-safe Claude tool use interactions. | Tools | Alex Albert | Apr 2024 | 
| Transcribe an audio file with Deepgram & use Anthropic to prepare interview questions! Apr 2024•IntegrationsMultimodal Transcribe audio with Deepgram and generate interview questions using Claude for preparation. | IntegrationsMultimodal | john-vajda | Apr 2024 | 
| Using the Wolfram Alpha LLM API as a tool with Claude Apr 2024•IntegrationsTools Integrate Wolfram Alpha LLM API as Claude tool for computational queries and answers. | IntegrationsTools | Alex Albert | Apr 2024 | 
| Using a calculator tool with Claude Provide Claude with calculator tool for arithmetic operations and mathematical problem solving. | Tools | Alex Albert | Apr 2024 | 
| Creating a customer service agent with client-side tools Apr 2024•ToolsAgent Patterns Build customer service chatbot with Claude using tools for customer lookup and order management. | ToolsAgent Patterns | Alex Albert | Apr 2024 | 
| Extracting structured JSON using Claude and tool use Extract structured JSON data from various inputs using Claude's tool use capabilities. | ResponsesTools | Alex Albert | Apr 2024 | 
| Metaprompt Prompt engineering tool that generates starting prompts for your tasks to solve blank-page problem. | Responses | Anthropic | Mar 2024 | 
| Citations Mar 2024•ResponsesRAG & Retrieval Enable Claude to provide detailed source citations when answering document-based questions for verification. | ResponsesRAG & Retrieval | Anthropic | Mar 2024 | 
| Claude 3 RAG agents with LangChain v1 Mar 2024•IntegrationsRAG & RetrievalAgent Patterns Build RAG agents with Claude 3 using LangChain v1's updated agent framework patterns. | IntegrationsRAG & RetrievalAgent Patterns | james-briggs | Mar 2024 | 
| Summarizing web page content with Claude 3 Haiku Fetch and summarize web page content using Claude 3 Haiku via URL extraction. | RAG & Retrieval | Alex Albert | Mar 2024 | 
| Using Haiku as a sub-agent Analyze financial reports using Haiku sub-agents for extraction and Opus for synthesis. | Agent Patterns | Alex Albert | Mar 2024 | 
| Multi-modal Mar 2024•IntegrationsMultimodal Use LlamaIndex's Anthropic MultiModal LLM abstraction for image understanding and reasoning. | IntegrationsMultimodal | Ravi Theja | Mar 2024 | 
| How to build a RAG system using Claude 3 and MongoDB Mar 2024•IntegrationsRAG & Retrieval Build chatbot RAG system with Claude and MongoDB using tech news as knowledge base. | IntegrationsRAG & Retrieval | Richmond Alake | Mar 2024 | 
| Building evals Build robust evaluation systems to measure and improve Claude's performance on key metrics. | Evals | Alex Albert | Mar 2024 | 
| Building a moderation filter with Claude Build customizable content moderation filters by defining rules and categories in prompts. | Responses | Alex Albert | Mar 2024 | 
| Prompting Claude for "JSON mode" Get reliable JSON output from Claude using effective prompting techniques without constrained sampling. | Responses | Alex Albert | Mar 2024 | 
| How to make SQL queries with Claude Generate SQL queries from natural language questions using Claude with database schema context. | RAG & Retrieval | Alex Albert | Mar 2024 | 
| Getting started - how to pass images into Claude Tutorial on passing images to Claude 3 API for vision-based text analysis. | Multimodal | Alex Albert | Mar 2024 | 
| How to transcribe documents with Claude Extract and structure unstructured text from images and PDFs using Claude 3's vision. | Multimodal | Alex Albert | Mar 2024 | 
| Working with charts, graphs, and slide decks Extract insights from charts, graphs, and presentations using Claude's vision analysis capabilities. | Multimodal | Alex Albert | Mar 2024 | 
| Multi-document agents Mar 2024•IntegrationsRAG & RetrievalAgent Patterns Build RAG for large document collections using DocumentAgents with ReAct Agent pattern. | IntegrationsRAG & RetrievalAgent Patterns | Ravi Theja | Mar 2024 | 
| ReAct agent Mar 2024•IntegrationsAgent PatternsTools Create ReAct agents with LlamaIndex for tool-based reasoning and action workflows. | IntegrationsAgent PatternsTools | Ravi Theja | Mar 2024 | 
| RAG pipeline with LlamaIndex Mar 2024•IntegrationsRAG & Retrieval Build basic RAG pipeline with LlamaIndex for document retrieval and question answering. | IntegrationsRAG & Retrieval | Ravi Theja | Mar 2024 | 
| RouterQuery engine Mar 2024•IntegrationsRAG & Retrieval Route queries to different indices using LlamaIndex RouterQueryEngine for multi-document search. | IntegrationsRAG & Retrieval | Ravi Theja | Mar 2024 | 
| SubQuestionQueryEngine Mar 2024•IntegrationsRAG & Retrieval Decompose complex queries into sub-questions across multiple documents using LlamaIndex engine. | IntegrationsRAG & Retrieval | Ravi Theja | Mar 2024 | 
| Retrieval-augmented generation using Pinecone Feb 2024•IntegrationsRAG & Retrieval Connect Claude with Pinecone vector database for retrieval-augmented generation and semantic search. | IntegrationsRAG & Retrieval | Alex Albert | Feb 2024 | 
| "Uploading" PDFs to Claude via the API Process and summarize PDF documents using Claude API with text extraction and encoding. | RAG & Retrieval | Anthropic | Aug 2023 | 
| Iteratively searching Wikipedia with Claude Legacy notebook showing iterative Wikipedia searches with Claude 2 for research workflows. | Integrations | Anthropic | Aug 2023 |

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

- Source: [https://platform.claude.com/cookbooks](https://platform.claude.com/cookbooks)
