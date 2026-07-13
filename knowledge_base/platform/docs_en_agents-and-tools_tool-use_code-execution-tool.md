---
title: "Code execution tool - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool"
library: "platform"
created: "2026-07-13T07:46:35.188862+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files, including writing code, in a secure, sandboxed environment.

**Code execution is free when used with web search or web fetch ( web_search_20260209, web_fetch_20260209, or later).** When one of those tools is in your request, there are no additional charges for code execution in that request beyond standard token costs. This covers both the code execution behind dynamic filtering and any code Claude runs directly. Standard code execution pricing applies when they are not included.

Code execution also powers dynamic filtering in the web search and web fetch tools: Claude filters results inside the code execution environment before they reach the context window. When dynamic filtering runs, the API provisions the code execution it needs for the request automatically, so you don't add the code execution tool to your request for it.

Reach out through the feedback form to share your feedback on this feature.

This feature is **not** eligible for Zero Data Retention (ZDR). Data is retained according to the feature's standard retention policy.

The code execution tool is available on the following models:

| Model | Tool versions | 
|---|---|
| Claude Fable 5 (claude-fable-5) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Mythos 5 (claude-mythos-5) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Sonnet 5 (claude-sonnet-5) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Opus 4.8 (claude-opus-4-8) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Opus 4.7 (claude-opus-4-7) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Opus 4.6 (claude-opus-4-6) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Sonnet 4.6 (claude-sonnet-4-6) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Opus 4.5 (claude-opus-4-5-20251101) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Haiku 4.5 (claude-haiku-4-5-20251001) | `code_execution_20250825`,`code_execution_20260120`,`code_execution_20260521` | 
| Claude Opus 4.1 (claude-opus-4-1-20250805) (deprecated) | `code_execution_20250825` | 

Each tool version builds on the previous one:

`code_execution_20250825` supports Bash commands and file operations and is available on every model in the table.`code_execution_20260120` adds REPL state persistence and programmatic tool calling from within the sandbox. Claude Haiku 4.5 accepts the `code_execution_20260120` and `code_execution_20260521` tool types, but programmatic tool calling and the REPL state persistence that depends on it aren't available on it, so the newer versions behave like `code_execution_20250825` there.`code_execution_20260521` is the same runtime as `code_execution_20260120`. The difference is that the tool description tells Claude about the 90-second wall-clock limit on each Python cell in programmatic tool calling, so Claude can budget long-running cells. A cell that exceeds the limit returns a normal code execution result with a non-zero `return_code` and a `detection_timeout` status message in its output. This is separate from the `execution_time_exceeded` error code, which the API returns when a whole tool invocation exceeds the maximum execution time.All three tool versions are generally available and don't require an `anthropic-beta` header. The legacy code execution beta headers remain valid opt-ins.

The examples on this page use `code_execution_20250825` because every model in the table supports it. The current web search and web fetch tools (`web_search_20260209`, `web_fetch_20260209`, and later) require `code_execution_20260120` or later as their code execution version.

If you're still using the legacy `code_execution_20250522` (Python only), see Upgrade to latest tool version to migrate from it.

Older tool versions are not guaranteed to be backwards-compatible with newer models. Always use the tool version that corresponds to your model version.

Code execution is available on:

Code execution is not currently available on Amazon Bedrock or Google Cloud.

For Claude Mythos Preview, code execution is supported on the Claude API and Microsoft Foundry only. It is not available for Mythos Preview on Amazon Bedrock, Google Cloud, or Claude Platform on AWS.

Here's a simple example that asks Claude to perform a calculation:

```
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Use the code execution tool to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
print(response.to_json())
```
The response interleaves `server_tool_use` blocks (the commands Claude ran) with their tool result blocks, followed by Claude's text. The top level also includes a `container` object whose `id` you can reuse across requests. See Response format for the block shapes.

When you add the code execution tool to your API request:

`tool_result` blocks yourself. One exception is when Claude calls one of your client tools alongside code execution: the API returns the code execution call without its result. The result arrives in a later response, after you send back the `tool_result` blocks for your client toolsThe container has Python pre-installed. Claude writes Python with the file operations sub-tool and runs it with a Bash command. With `code_execution_20260120` or later and programmatic tool calling, the Python interpreter state (such as variable bindings) also persists across requests that reuse the container.

Claude runs code when the request benefits from computation or file handling:

Claude answers directly without running code for:

If you want Claude to run code for a borderline request, ask explicitly (for example, "run code to verify this").

To analyze your own data files (such as CSV, Excel, or images), upload them through the Files API and reference them in your request:

Using the Files API with Code Execution requires the Files API beta header: `"anthropic-beta": "files-api-2025-04-14"`

The Python environment can process various file types uploaded through the Files API, including:

`container_upload` content block```
client = anthropic.Anthropic()
# Upload a file
file_object = client.beta.files.upload(file=Path("data.csv"))
# Use the file_id with code execution
response = client.beta.messages.create(
    model="claude-opus-4-8",
    betas=["files-api-2025-04-14"],
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this CSV data"},
                {"type": "container_upload", "file_id": file_object.id},
            ],
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
print(response.to_json())
```
When Claude creates files during code execution, each created file's ID appears in the code execution tool result, and you can download it with the Files API:

```
client = Anthropic()
# Request code execution that creates files
response = client.beta.messages.create(
    model="claude-opus-4-8",
    betas=["files-api-2025-04-14"],
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Create a matplotlib visualization and save it as output.png",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
# Extract file IDs from the response
def extract_file_ids(response: BetaMessage) -> list[str]:
    file_ids: list[str] = []
    for item in response.content:
        if item.type == "bash_code_execution_tool_result":
            content_item = item.content
            if content_item.type == "bash_code_execution_result":
                for output_block in content_item.content:
                    file_ids.append(output_block.file_id)
    return file_ids
# Download the created files
for file_id in extract_file_ids(response):
    file_metadata = client.beta.files.retrieve_metadata(file_id)
    file_content = client.beta.files.download(file_id)
    file_content.write_to_file(file_metadata.filename)
    print(f"Downloaded: {file_metadata.filename}")
```
The code execution tool requires no additional parameters:

```
{
  "type": "code_execution_20250825",
  "name": "code_execution"
}
```
Both fields are fixed: `type` selects the tool version, and `name` must be `code_execution`.

When this tool is provided, Claude automatically gains access to two sub-tools:

`bash_code_execution`: Run shell commands`text_editor_code_execution`: View, create, and edit files, including writing codeWhen Claude runs code, the response also includes a top-level `container` object with the container's `id` and `expires_at` timestamp. Pass that ID back in the top-level `container` request parameter to keep using the same container. See Container reuse.

The code execution tool can return two types of results depending on the operation:

```
{
  "type": "server_tool_use",
  "id": "srvtoolu_01B3C4D5E6F7G8H9I0J1K2L3",
  "name": "bash_code_execution",
  "input": {
    "command": "ls -la | head -5"
  }
},
{
  "type": "bash_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01B3C4D5E6F7G8H9I0J1K2L3",
  "content": {
    "type": "bash_code_execution_result",
    "stdout": "total 24\ndrwxr-xr-x 2 user user 4096 Jan 1 12:00 .\ndrwxr-xr-x 3 user user 4096 Jan 1 11:00 ..\n-rw-r--r-- 1 user user  220 Jan 1 12:00 data.csv\n-rw-r--r-- 1 user user  180 Jan 1 12:00 config.json",
    "stderr": "",
    "return_code": 0,
    "content": []
  }
}
```
**View file:**

```
{
  "type": "server_tool_use",
  "id": "srvtoolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "name": "text_editor_code_execution",
  "input": {
    "command": "view",
    "path": "config.json"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "content": {
    "type": "text_editor_code_execution_view_result",
    "file_type": "text",
    "content": "{\n  \"setting\": \"value\",\n  \"debug\": true\n}",
    "num_lines": 4,
    "start_line": 1,
    "total_lines": 4
  }
}
```
**Create file:**

```
{
  "type": "server_tool_use",
  "id": "srvtoolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "name": "text_editor_code_execution",
  "input": {
    "command": "create",
    "path": "new_file.txt",
    "file_text": "Hello, World!"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01D5E6F7G8H9I0J1K2L3M4N5",
  "content": {
    "type": "text_editor_code_execution_create_result",
    "is_file_update": false
  }
}
```
**Edit file (str_replace):**

```
{
  "type": "server_tool_use",
  "id": "srvtoolu_01E6F7G8H9I0J1K2L3M4N5O6",
  "name": "text_editor_code_execution",
  "input": {
    "command": "str_replace",
    "path": "config.json",
    "old_str": "\"debug\": true",
    "new_str": "\"debug\": false"
  }
},
{
  "type": "text_editor_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01E6F7G8H9I0J1K2L3M4N5O6",
  "content": {
    "type": "text_editor_code_execution_str_replace_result",
    "old_start": 3,
    "old_lines": 1,
    "new_start": 3,
    "new_lines": 1,
    "lines": ["-  \"debug\": true", "+  \"debug\": false"]
  }
}
```
Bash command results (`bash_code_execution_result`) include:

`stdout`: Output from successful execution`stderr`: Error messages if execution fails`return_code`: 0 for success, non-zero for failure`content`: A list with an entry for each file the command created. Each entry carries the `file_id` to retrieve the file with the Files APIFile operation results have their own fields:

`text_editor_code_execution_view_result`): `file_type`, `content`, `num_lines`, `start_line`, `total_lines``text_editor_code_execution_create_result`): `is_file_update` (whether the file already existed)`text_editor_code_execution_str_replace_result`): `old_start`, `old_lines`, `new_start`, `new_lines`, `lines` (diff format)Each tool type can return specific errors:

**Common errors (all tools):**

```
{
  "type": "bash_code_execution_tool_result",
  "tool_use_id": "srvtoolu_01VfmxgZ46TiHbmXgy928hQR",
  "content": {
    "type": "bash_code_execution_tool_result_error",
    "error_code": "unavailable"
  }
}
```
**Error codes by tool type:**

| Tool | Error code | Description | 
|---|---|---|
| All tools | `unavailable` | The tool is temporarily unavailable | 
| All tools | `execution_time_exceeded` | The tool invocation exceeded the maximum execution time | 
| All tools | `invalid_tool_input` | Invalid parameters provided to the tool | 
| All tools | `too_many_requests` | Rate limit exceeded for tool usage | 
| bash | `output_file_too_large` | Command output exceeded the maximum size | 
| text_editor | `file_not_found` | File doesn't exist (for view/edit operations) | 

An expired container can't be reused: requests that reference it return an error instead of restoring it. Send the request again without the `container` parameter to get a new container.

`pause_turn` stop reasonThe response might include a `pause_turn` stop reason, which indicates that the API paused a long-running turn. You may
provide the response back as-is in a subsequent request to let Claude continue its turn, or modify the content if you
want to interrupt the conversation.

The code execution tool runs in a secure, containerized environment designed specifically for code execution, with a higher focus on Python.

`execution_time_exceeded` error. With programmatic tool calling, each REPL cell also has a 90-second wall-clock limitThe sandboxed Python environment includes these commonly used libraries:

The container also includes command-line tools such as unzip, unrar, 7zip, bc, rg (ripgrep), fd, and sqlite.

The container has no internet access, so Claude can't download or install additional packages at runtime: only the pre-installed libraries are available.

You can reuse an existing container across multiple API requests by providing the container ID from a previous response.
This allows you to maintain created files between requests. With `code_execution_20260120` or later and programmatic tool calling, the Python interpreter state persists as well.

Containers expire 30 days after creation. After about five minutes of inactivity a container is checkpointed, and sending a request with its ID inside the 30-day window restores it. The `expires_at` timestamp in the response's `container` object is a shorter rolling value and doesn't report the 30-day limit. A container that has expired can't be reused. Send the request again without the `container` parameter to get a new container.

```
client = anthropic.Anthropic()
# First request: create a file with a random number in a new container
response1 = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Write a file with a random number and save it to '/tmp/number.txt'",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
# Second request: pass the container ID back so Claude reuses the same container
response2 = client.messages.create(
    container=response1.container.id,
    model="claude-opus-4-8",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Read the number from '/tmp/number.txt' and calculate its square",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
print(response2.to_json())
```
When you provide code execution alongside client-provided tools that also run code (such as a Bash tool or custom REPL), Claude is operating in a multi-computer environment. The code execution tool runs in Anthropic's sandboxed container, while your client-provided tools run in a separate environment that you control. Claude can sometimes confuse these environments, attempting to use the wrong tool or assuming state is shared between them.

To avoid this, add instructions to your system prompt that clarify the distinction:

```
When multiple code execution environments are available, be aware that:
- Variables, files, and state do NOT persist between different execution environments
- Use the code_execution tool for general-purpose computation in Anthropic's sandboxed environment
- Use client-provided execution tools (e.g., bash) when you need access to the user's local system, files, or data
- If you need to pass results between environments, explicitly include outputs in subsequent tool calls rather than assuming shared state
```
This is especially important when combining code execution with web search or web fetch, which enable code execution automatically. If your application already provides a client-side shell tool, the automatic code execution creates a second execution environment that Claude needs to distinguish between.

When Claude calls one of your client tools alongside code execution, the API returns the code execution call without its result. The result arrives in a later response, after you send back the `tool_result` blocks for your client tools.

With streaming enabled (`"stream": true`), you'll receive code execution events as they occur. The sub-tool input streams as `input_json_delta` events, and each result block arrives whole in a single `content_block_start` event:

```
event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "server_tool_use", "id": "srvtoolu_xyz789", "name": "bash_code_execution"}}
// Tool input streamed as partial JSON
event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "input_json_delta", "partial_json": "{\"command\": \"python analyze.py\"}"}}
// Pause while the command runs
// Execution result delivered as a complete block
event: content_block_start
data: {"type": "content_block_start", "index": 2, "content_block": {"type": "bash_code_execution_tool_result", "tool_use_id": "srvtoolu_xyz789", "content": {"type": "bash_code_execution_result", "stdout": "   A  B  C\n0  1  2  3\n1  4  5  6", "stderr": "", "return_code": 0, "content": []}}}
```
You can include the code execution tool in the Messages Batches API. Code execution tool calls through the Messages Batches API are priced the same as those in regular Messages API requests.

**Code execution is free when used with web search or web fetch.** When `web_search_20260209` (or later) or `web_fetch_20260209` (or later) is included in your API request, there are no additional charges for code execution tool calls beyond the standard input and output token costs.

When used without these tools, code execution is billed by execution time, tracked separately from token usage:

Code execution usage is tracked in the response:

```
{
  "usage": {
    "input_tokens": 105,
    "output_tokens": 239,
    "server_tool_use": {
      "code_execution_requests": 1
    }
  }
}
```
The latest tool version is `code_execution_20260521`. To move between the three current versions, update the `type` string in your request: all three return the response blocks documented in Response format. See Model compatibility for what each version adds and which models support it.

The rest of this section covers migrating from the legacy Python-only `code_execution_20250522` to the current tool versions.

| Component | Legacy | Current | 
|---|---|---|
| Beta header | `code-execution-2025-05-22` | None required | 
| Tool type | `code_execution_20250522` | `code_execution_20250825`or later | 
| Capabilities | Python only | Bash commands, file operations | 
| Response types | `code_execution_result` | `bash_code_execution_result`,`text_editor_code_execution_*_result` | 

To upgrade, update the tool type in your API requests:

```
- "type": "code_execution_20250522"
+ "type": "code_execution_20250825"
```
**Review response handling** (if parsing responses programmatically):

Code execution runs in server-side sandbox containers. Container data, including execution artifacts, uploaded files, and outputs, is retained for up to 30 days. This retention applies to all data processed within the container environment. Files that code execution creates in the Files API (retrievable with `client.beta.files.download()`) persist until explicitly deleted.

For ZDR eligibility across all features, see API and data retention.

Pair a faster executor model with a higher-intelligence advisor model that provides strategic guidance mid-generation.

Call your own tools from code that runs inside the code execution container.

Upload files for analysis and download the files that code execution creates.

Learn how to use Agent Skills to extend Claude's capabilities through the API.

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

- Source: [https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
