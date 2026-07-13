---
title: "Search results - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/search-results"
library: "platform"
created: "2026-07-13T08:00:49.144079+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This feature is eligible for Zero Data Retention (ZDR). When your organization has a ZDR arrangement, data sent through this feature is not stored after the API response is returned.

Search result content blocks enable natural citations with proper source attribution, bringing web search-quality citations to your custom applications. This feature is particularly powerful for RAG (Retrieval-Augmented Generation) applications where you need Claude to cite sources accurately.

The search results feature is available on the following models:

`claude-opus-4-7`)`claude-opus-4-6`)`claude-sonnet-5`)`claude-sonnet-4-6`)`claude-sonnet-4-5-20250929`)`claude-opus-4-5-20251101`)`claude-opus-4-1-20250805`)`claude-opus-4-20250514`)`claude-sonnet-4-20250514`)`claude-haiku-4-5-20251001`)`claude-3-5-haiku-20241022`)Search results can be provided in two ways:

In both cases, Claude can automatically cite information from the search results with proper source attribution.

Search results use the following structure:

```
{
  "type": "search_result",
  "source": "https://example.com/article", // Required: Source URL or identifier
  "title": "Article Title", // Required: Title of the result
  "content": [
    // Required: Array of text blocks
    {
      "type": "text",
      "text": "The actual content of the search result..."
    }
  ],
  "citations": {
    // Optional: Citation configuration
    "enabled": true // Enable/disable citations for this result
  }
}
```
| Field | Type | Description | 
|---|---|---|
| `type` | string | Must be `"search_result"` | 
| `source` | string | The source URL or identifier for the content | 
| `title` | string | A descriptive title for the search result | 
| `content` | array | An array of text blocks containing the actual content | 

| Field | Type | Description | 
|---|---|---|
| `citations` | object | Citation configuration with `enabled`boolean field | 
| `cache_control` | object | Cache control settings (e.g., `{"type": "ephemeral"}`) | 

Each item in the `content` array must be a text block with:

`type`: Must be `"text"``text`: The actual text content (non-empty string)The most powerful use case is returning search results from your custom tools. This enables dynamic RAG applications where tools fetch and return relevant content with automatic citations.

```
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    SearchResultBlockParam,
    ToolResultBlockParam,
)
client = Anthropic()
# Define a knowledge base search tool
knowledge_base_tool = {
    "name": "search_knowledge_base",
    "description": "Search the company knowledge base for information",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The search query"}},
        "required": ["query"],
    },
}
# Function to handle the tool call
def search_knowledge_base(query):
    # Your search logic here
    # Returns search results in the correct format
    return [
        SearchResultBlockParam(
            type="search_result",
            source="https://docs.company.com/product-guide",
            title="Product Configuration Guide",
            content=[
                TextBlockParam(
                    type="text",
                    text="To configure the product, navigate to Settings > Configuration. The default timeout is 30 seconds, but can be adjusted between 10-120 seconds based on your needs.",
                )
            ],
            citations={"enabled": True},
        ),
        SearchResultBlockParam(
            type="search_result",
            source="https://docs.company.com/troubleshooting",
            title="Troubleshooting Guide",
            content=[
                TextBlockParam(
                    type="text",
                    text="If you encounter timeout errors, first check the configuration settings. Common causes include network latency and incorrect timeout values.",
                )
            ],
            citations={"enabled": True},
        ),
    ]
# Create a message with the tool
response = client.messages.create(
    model="claude-opus-4-8",  # Works with all supported models
    max_tokens=1024,
    tools=[knowledge_base_tool],
    messages=[
        MessageParam(role="user", content="How do I configure the timeout settings?")
    ],
)
# When Claude calls the tool, provide the search results
if response.content[0].type == "tool_use":
    tool_result = search_knowledge_base(response.content[0].input["query"])
    # Send the tool result back
    final_response = client.messages.create(
        model="claude-opus-4-8",  # Works with all supported models
        max_tokens=1024,
        messages=[
            MessageParam(
                role="user", content="How do I configure the timeout settings?"
            ),
            MessageParam(role="assistant", content=response.content),
            MessageParam(
                role="user",
                content=[
                    ToolResultBlockParam(
                        type="tool_result",
                        tool_use_id=response.content[0].id,
                        content=tool_result,  # Search results go here
                    )
                ],
            ),
        ],
    )
```
You can also provide search results directly in user messages. This is useful for:

```
from anthropic.types import MessageParam, TextBlockParam, SearchResultBlockParam
client = Anthropic()
# Provide search results directly in the user message
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        MessageParam(
            role="user",
            content=[
                SearchResultBlockParam(
                    type="search_result",
                    source="https://docs.company.com/api-reference",
                    title="API Reference - Authentication",
                    content=[
                        TextBlockParam(
                            type="text",
                            text="All API requests must include an API key in the Authorization header. Keys can be generated from the dashboard. Rate limits: 1000 requests per hour for standard tier, 10000 for premium.",
                        )
                    ],
                    citations={"enabled": True},
                ),
                SearchResultBlockParam(
                    type="search_result",
                    source="https://docs.company.com/quickstart",
                    title="Getting Started Guide",
                    content=[
                        TextBlockParam(
                            type="text",
                            text="To get started: 1) Sign up for an account, 2) Generate an API key from the dashboard, 3) Install our SDK using pip install company-sdk, 4) Initialize the client with your API key.",
                        )
                    ],
                    citations={"enabled": True},
                ),
                TextBlockParam(
                    type="text",
                    text="Based on these search results, how do I authenticate API requests and what are the rate limits?",
                ),
            ],
        )
    ],
)
print(response)
```
Regardless of how search results are provided, Claude automatically includes citations when using information from them:

```
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "All API requests must include an API key in the Authorization header. Keys can be generated from the dashboard.",
      "citations": [
        {
          "type": "search_result_location",
          "cited_text": "All API requests must include an API key in the Authorization header. Keys can be generated from the dashboard. Rate limits: 1000 requests per hour for standard tier, 10000 for premium.",
          "source": "https://docs.company.com/api-reference",
          "title": "API Reference - Authentication",
          "search_result_index": 0,
          "start_block_index": 0,
          "end_block_index": 1
        }
      ]
    },
    {
      "type": "text",
      "text": "\n\nTo set this up from scratch, you'll need to "
    },
    {
      "type": "text",
      "text": "sign up for an account, generate an API key from the dashboard, install the SDK using `pip install company-sdk`, and initialize the client with your API key.",
      "citations": [
        {
          "type": "search_result_location",
          "cited_text": "To get started: 1) Sign up for an account, 2) Generate an API key from the dashboard, 3) Install our SDK using pip install company-sdk, 4) Initialize the client with your API key.",
          "source": "https://docs.company.com/quickstart",
          "title": "Getting Started Guide",
          "search_result_index": 1,
          "start_block_index": 0,
          "end_block_index": 1
        }
      ]
    }
  ]
}
```
Each citation includes:

| Field | Type | Description | 
|---|---|---|
| `type` | string | Always `"search_result_location"`for search result citations | 
| `source` | string | The source from the original search result | 
| `title` | string or null | The title from the original search result | 
| `cited_text` | string | The full text of the cited block(s), concatenated. Equals the contents of `content[start_block_index:end_block_index]`joined together. Not counted toward output tokens. | 
| `search_result_index` | integer | 0-based index of the cited search result among all `search_result`blocks in the request, in the order they appear (across all messages and tool results). | 
| `start_block_index` | integer | 0-based index of the first cited block in the search result's `content`array. | 
| `end_block_index` | integer | Exclusive end index of the cited block range in the search result's `content`array. Always greater than`start_block_index`. | 

The block indices identify a slice of the search result's `content` array, and `cited_text` is the full text of that slice. The text block is the minimal citable unit: Claude cites whole blocks, not substrings within a block. To get finer-grained citations, split your search result content into smaller blocks (see Multiple content blocks).

Search results can contain multiple text blocks in the `content` array:

```
{
  "type": "search_result",
  "source": "https://docs.company.com/api-guide",
  "title": "API Documentation",
  "content": [
    {
      "type": "text",
      "text": "Authentication: All API requests require an API key."
    },
    {
      "type": "text",
      "text": "Rate Limits: The API allows 1000 requests per hour per key."
    },
    {
      "type": "text",
      "text": "Error Handling: The API returns standard HTTP status codes."
    }
  ]
}
```
A citation referencing the rate limits block looks like:

```
{
  "type": "search_result_location",
  "cited_text": "Rate Limits: The API allows 1000 requests per hour per key.",
  "source": "https://docs.company.com/api-guide",
  "title": "API Documentation",
  "search_result_index": 0,
  "start_block_index": 1,
  "end_block_index": 2
}
```
When this search result is cited, `start_block_index` and `end_block_index` identify which of these blocks the citation covers, and `cited_text` contains exactly those blocks' text. Splitting content into smaller, focused blocks gives Claude finer citation boundaries; combining content into one block means every citation returns the full text. This is the same model used by custom content documents in the Citations feature.

You can use both tool-based and top-level search results in the same conversation:

```
from anthropic.types import MessageParam, SearchResultBlockParam, TextBlockParam
# First message with top-level search results
messages = [
    MessageParam(
        role="user",
        content=[
            SearchResultBlockParam(
                type="search_result",
                source="https://docs.company.com/overview",
                title="Product Overview",
                content=[
                    TextBlockParam(
                        type="text", text="Our product helps teams collaborate..."
                    )
                ],
                citations={"enabled": True},
            ),
            TextBlockParam(
                type="text",
                text="Tell me about this product and search for pricing information",
            ),
        ],
    )
]
# Claude might respond and call a tool to search for pricing
# Then you provide tool results with more search results
```
Both methods support mixing search results with other content:

```
from anthropic.types import SearchResultBlockParam, TextBlockParam
# In tool results
tool_result = [
    SearchResultBlockParam(
        type="search_result",
        source="https://docs.company.com/guide",
        title="User Guide",
        content=[TextBlockParam(type="text", text="Configuration details...")],
        citations={"enabled": True},
    ),
    TextBlockParam(
        type="text", text="Additional context: This applies to version 2.0 and later."
    ),
]
# In top-level content
user_content = [
    SearchResultBlockParam(
        type="search_result",
        source="https://research.com/paper",
        title="Research Paper",
        content=[TextBlockParam(type="text", text="Key findings...")],
        citations={"enabled": True},
    ),
    {
        "type": "image",
        "source": {"type": "url", "url": "https://example.com/chart.png"},
    },
    TextBlockParam(
        type="text", text="How does the chart relate to the research findings?"
    ),
]
```
Add cache control for better performance:

```
{
  "type": "search_result",
  "source": "https://docs.company.com/guide",
  "title": "User Guide",
  "content": [{ "type": "text", "text": "..." }],
  "cache_control": {
    "type": "ephemeral"
  }
}
```
By default, citations are disabled for search results. You can enable citations by explicitly setting the `citations` configuration:

```
{
  "type": "search_result",
  "source": "https://docs.company.com/guide",
  "title": "User Guide",
  "content": [{ "type": "text", "text": "Important documentation..." }],
  "citations": {
    "enabled": true // Enable citations for this result
  }
}
```
When `citations.enabled` is set to `true`, Claude includes citation references when using information from the search result. This enables:

Citations are all-or-nothing: either all search results in a request must have citations enabled, or all must have them disabled. Mixing search results with different citation settings results in an error.

**Structure results effectively:**

**Maintain consistency:**

**Handle errors gracefully:**

```
def search_with_fallback(query):
    try:
        results = perform_search(query)
        if not results:
            return {"type": "text", "text": "No results found."}
        return format_as_search_results(results)
    except Exception as e:
        return {"type": "text", "text": f"Search error: {str(e)}"}
```
`content` array must contain at least one text blockLearn how citations work across documents, custom content, and search results.

Let Claude search the web and cite sources automatically using a server tool.

See the complete Messages API documentation, including content block types.

Cache search results with `cache_control` to reduce cost and latency on repeated requests.

Was this page helpful?

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/search-results](https://platform.claude.com/docs/en/build-with-claude/search-results)
