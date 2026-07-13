---
title: "Vision - Claude Platform Docs"
url: "https://platform.claude.com/docs/en/build-with-claude/vision"
library: "platform"
created: "2026-07-13T07:45:02.003590+00:00"
---

# Overview

We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.

This guide describes how to send images to Claude, the limits and costs that apply, and where to find guidance for coordinate-based workflows.

Use Claude's vision capabilities through:

On the API, provide images to Claude as `image` content blocks using one of three source types:

`file_id` returned by the Files API (upload once, reference many times)On Amazon Bedrock and Google Cloud, only base64-encoded sources are currently available.

Just as placing long documents before your query improves results in text prompts, Claude works best when images come before text. Images placed after text or interpolated with text still perform well, but if your use case allows it, prefer an image-then-text structure.

```
image1_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
image1_media_type = "image/png"
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image1_media_type,
                        "data": image1_data,
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
print(message)
```
```
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg",
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
print(message)
```
For images you'll use repeatedly or when you want to avoid encoding overhead, use the Files API. Upload the image once, then reference the returned `file_id` in subsequent messages instead of resending base64 data.

In multi-turn conversations and agentic workflows, each request resends the
full conversation history. If images are base64-encoded, the full image bytes
are included in the payload on every turn, which can significantly increase
request size and latency as the conversation grows. Uploading images to the
Files API and referencing them by `file_id` keeps request payloads small
regardless of how many images accumulate in the conversation history.

```
client = anthropic.Anthropic()
# Upload the image file
with open("image.jpg", "rb") as f:
    file_upload = client.beta.files.upload(file=("image.jpg", f, "image/jpeg"))
# Use the uploaded file in a message
message = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    betas=["files-api-2025-04-14"],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "file", "file_id": file_upload.id},
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
print(message.content)
```
See Messages API examples for more example code and parameter details.

You can include multiple images in a single request, and Claude analyzes them jointly. This is useful for comparing images, asking about differences, or working with a sequence such as pages of a document. When sending several images, introduce each one with a short text label (`Image 1:`, `Image 2:`, and so on) so you can refer to them by name in your prompt and in follow-up turns.

```
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Image 1:"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC",
                    },
                },
                {"type": "text", "text": "Image 2:"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC",
                    },
                },
                {"type": "text", "text": "How are these images different?"},
            ],
        }
    ],
)
print(message)
```
In a multi-turn conversation, add new images in later `user` turns the same way. Claude has access to every image from earlier turns, so follow-up questions such as "Are these similar to the first two?" work without including the earlier images again in the new turn's content.

The maximum number of images per message or request is:

The maximum dimensions per image are 8000x8000 px.

If a single API request contains more than 20 images, a stricter per-image dimension limit applies. On Amazon Bedrock and Google Cloud, document blocks such as PDFs also count toward this threshold. Images exceeding the stricter limit are rejected with an `invalid_request_error` whose message references "many-image requests" and states the current limit in pixels. To stay under the limit on all platforms, either resize each image so that neither dimension exceeds 2000 px, or keep the request to 20 or fewer image and document blocks.

The maximum size per image is:

Although the API supports up to 600 images per request, request size limits (32 MB for standard endpoints; lower on some partner-operated platforms, for example, Amazon Bedrock and Google Cloud) can be reached first. For many images, consider uploading with the Files API and referencing by `file_id` to keep request payloads small.

Even when using the Files API, requests with many large images can fail before reaching the 600-image count. Reduce image dimensions or file sizes (for example, by downsampling) before uploading (see Resolution and token cost).

Claude supports JPEG, PNG, GIF, and WebP images (`image/jpeg`, `image/png`, `image/gif`, `image/webp`). Animations are unsupported, and only the first frame is used.

Claude views images in patches instead of pixels. Each patch is a 28×28-pixel block of the image, referred to as a visual token. An image, therefore, costs `⌈width / 28⌉ × ⌈height / 28⌉` visual tokens.

Each model has a maximum native image resolution, expressed as a long-edge limit and a visual-token limit. Images larger than either limit are downscaled before processing; see How Claude resizes and pads images for the exact rule.

| Resolution tier | Models | Max long edge | Max visual tokens | 
|---|---|---|---|
| High-resolution | Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Opus 4.7, Claude Sonnet 5 | 2576 px | 4784 | 
| Standard | All other models | 1568 px | 1568 | 

High-resolution support is automatic on the listed models and requires no beta header or client-side opt-in.

The following table shows the visual-token cost for several image sizes on each tier:

| Image size | Standard-tier tokens | High-resolution-tier tokens | 
|---|---|---|
| 200x200 px (0.04 megapixels) | 64 | 64 | 
| 1000x1000 px (1 megapixel) | 1296 | 1296 | 
| 1092x1092 px (1.19 megapixels) | 1521 | 1521 | 
| 1920x1080 px (2.07 megapixels) | 1560 | 2691 | 
| 2000x1500 px (3 megapixels) | 1564 | 3888 | 
| 3840x2160 px (8.29 megapixels) | 1560 | 4784 | 

To estimate cost, multiply the token count by the per-token price of the model you're using. For example, at Claude Haiku 4.5's $1 per million input tokens (standard tier), the 1000×1000 image costs about $1.30 per thousand images. At Claude Opus 4.8's $5 per million (high-resolution tier), the same image costs about $6.48 per thousand and the 4K image about $23.92 per thousand.

High-resolution images can use up to roughly three times more visual tokens than the same image on a standard-tier model. If you don't need the additional fidelity that high resolution provides for computer use, screenshot understanding, and dense documents, downsample images before sending to control token costs. To minimize latency and to simplify coordinate-based workflows, prefer resizing images before uploading them.

When providing images to Claude, keep the following in mind for best results:

For bounding boxes, points, and pixel coordinates, see Coordinates and bounding boxes. Claude returns absolute pixel coordinates relative to the image it sees after resizing; that guide covers how Claude resizes and pads images and how to pre-resize or rescale so coordinates line up with your original image.

Although Claude's image understanding capabilities are cutting-edge, there are some limitations to be aware of:

Always carefully review and verify Claude's image interpretations, especially for high-stakes use cases. Do not use Claude for tasks requiring perfect precision or sensitive image analysis without human oversight.

Get tips and best-practice techniques for tasks such as interpreting charts and extracting content from forms.

See the Messages API documentation, including example API calls involving images.

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

- Source: [https://platform.claude.com/docs/en/build-with-claude/vision](https://platform.claude.com/docs/en/build-with-claude/vision)
