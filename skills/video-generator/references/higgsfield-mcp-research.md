# Higgsfield MCP Research Notes

Firecrawl research performed on 2026-05-05.

## Public Higgsfield MCP Page

Source: `https://higgsfield.ai/mcp`

- The MCP endpoint is `https://mcp.higgsfield.ai`.
- The page describes Higgsfield MCP as an agent interface for image generation, video
  creation, character training, and asset management.
- It lists Seedance, Kling, and Veo as video models available through the Higgsfield
  creative surface.
- It says agents can specify a model themselves or let the agent choose one.
- It states generation is asynchronous and the agent polls for results.
- It states users can reference previous generations as inputs.

## Official Higgsfield JavaScript SDK

Source: `https://github.com/higgsfield-ai/higgsfield-js`

- The official SDK uses `subscribe(endpoint, options)` in the V2 client.
- It documents status polling via `/requests/{request_id}/status`.
- Documented statuses include `queued`, `in_progress`, `nsfw`, `failed`, and
  `completed`.
- It documents `uploadImage()` and generic `upload()` helpers for CDN upload.
- It includes an image-to-video example using `/v1/image2video/dop` with an
  `input_images` array.

Use SDK details only as fallback context when the MCP schema is incomplete. Prefer the
connected Higgsfield MCP tools for production generation.

## Third-Party MCP Server

Source: `https://github.com/geopopos/higgsfield_ai_mcp`

- The repository is not official Higgsfield infrastructure, but it documents one MCP
  server shape with tools named `generate_image`, `generate_video`,
  `get_generation_status`, `create_character`, and `list_characters`.
- Its `generate_video` documentation uses a public HTTPS `image_url`, a `motion_id`, an
  optional prompt, and quality choices for a DoP image-to-video route.
- Treat this as compatibility reconnaissance, not as the required interface for the
  official Higgsfield MCP at `https://mcp.higgsfield.ai`.

## Practical Implications

- Inspect the connected MCP tool schema before calling video generation.
- Cache whichever media handle the MCP returns: UUID, URL, request ID, or history ID.
- Log request/job IDs immediately.
- Poll asynchronously until a terminal status.
- Stop when a required role or parameter is absent instead of silently changing the
  production strategy.
