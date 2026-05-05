# Higgsfield Model Context Protocol (MCP) Research Notes

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
- It states the connector authenticates through the user's Higgsfield account rather
  than an API key.

## Official Higgsfield CLI Page

Source: `https://higgsfield.ai/cli`

- The CLI is installed with `npm install -g @higgsfield/cli`.
- Authentication is started with `higgsfield auth login`.
- Higgsfield's page recommends `npx skills add higgsfield-ai/skills` for agent skill
  setup.
- The page says the CLI handles authentication, uploads, and polling, including for
  Codex-like agents.
- Treat the CLI as operational fallback context. The `video-generator` skill should
  still prefer the connected Higgsfield MCP when available.

## Official Higgsfield API Docs

Sources: `https://docs.higgsfield.ai/index` and
`https://docs.higgsfield.ai/guides/video`

- The API documentation describes a unified platform for image, video, voice, and audio
  models.
- The image-to-video guide lists Higgsfield DoP preview,
  `bytedance/seedance/v1/pro/image-to-video`, and
  `kling-video/v2.1/pro/image-to-video` examples.
- The guide's direct HTTP example submits an `image_url`, `prompt`, and `duration`.
- The guide recommends high-quality source images, matching source and target aspect
  ratios, shorter iteration durations, stored request IDs, and webhooks for production
  workflows.
- API docs are useful for validating concepts such as request IDs, image URLs, and
  webhook/polling state, but they are not the live MCP schema.

## Official Higgsfield JavaScript SDK

Source: `https://github.com/higgsfield-ai/higgsfield-js`

- The official SDK uses `subscribe(endpoint, options)` in the V2 client.
- It documents status polling via `/requests/{request_id}/status`.
- Documented statuses include `queued`, `in_progress`, `nsfw`, `failed`, and
  `completed`.
- It documents `uploadImage()` and generic `upload()` helpers for CDN upload.
- It includes an image-to-video example using `/v1/image2video/dop` with an
  `input_images` array.
- It returns request/status/cancel fields and supports automatic polling.

Use SDK details only as fallback context when the MCP schema is incomplete. Prefer the
connected Higgsfield MCP tools for production generation.

## Seedance 2.0 Page

Source: `https://higgsfield.ai/seedance/2.0`

- Higgsfield positions Seedance 2.0 for multi-shot cinematic storytelling, character
  consistency, high-impact motion, and frame-level precision.
- The page says Seedance 2.0 can combine multiple references in one generation and
  generate clips up to 15 seconds per shot.
- It describes support for reference images, video clips, audio clips, and text prompts
  on the creative surface.
- Use this as model-selection evidence for character-centric, reference-heavy, and
  action/interpolation shots. Validate exact MCP model ID and accepted media roles at
  runtime.

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
- Prefer Seedance 2.0 for character, prop, and recurring-element continuity; prefer
  Kling-style routes when smooth camera travel matters more than visual identity.
- Cache whichever media handle the MCP returns: UUID, URL, request ID, or history ID.
- Log request/job IDs immediately.
- Poll asynchronously until a terminal status.
- Stop when a required role or parameter is absent instead of silently changing the
  production strategy.

## Firecrawl Follow-Up: 2026-05-05

Sources:

- `https://higgsfield.ai/ai-video`
- `https://higgsfield.ai/kling-3.0`
- `https://higgsfield.ai/ai/video?model=kling3_0`

Useful confirmations:

- Higgsfield's public video surface lists Seedance 2.0, Kling 3.0, Veo, Sora, Wan, and
  related models in one workspace.
- It presents first and last image references as a video control surface.
- It markets Seedance 2.0 in 1080p and Kling 3.0 in 4K.
- The Kling 3.0 surface describes native audio, multi-shot storyboarding with up to 6
  cuts, and up to 15-second generations.
- The Kling 3.0 UI scrape exposed start frame and end frame controls, a 5 s default,
  aspect ratios `16:9`, `9:16`, and `1:1`, and resolution choices `720p`, `1080p`, and
  `4K`.
- Higgsfield plan text advertises plan-level parallel video generation limits, such as
  2, 6, 8, or 16 parallel videos depending on plan.

Gaps still not confirmed by public pages:

- No public page exposed the live MCP `generate_video` schema.
- Firecrawl did not confirm per-call `count`; treat it as a live-schema-gated MCP field.
- Firecrawl did not confirm `cfg_scale` semantics; treat S01 observations as empirical
  working defaults that must be validated and logged per run.
- Public `1080p` or `4K` labels do not prove exact output pixels. Always measure the
  downloaded file.
