# Media Upload and State Tracking

Higgsfield MCP video generation cannot consume repo-relative paths directly unless the
connected tool explicitly supports local file uploads. The prompt manifest uses local
paths for reviewability, so generation must convert those paths into whatever media
handle the connected Higgsfield MCP accepts: uploaded media UUID, CDN URL, generation
history ID, or a tool-specific file input.

Use the Higgsfield MCP first. Higgsfield's public MCP page says agents can use previous
generations as inputs, and the official CLI page says the CLI handles authentication,
uploads, and polling for Codex-like agents. The official SDK documents `uploadImage()`
and generic `upload()` helpers for CDN upload. Treat CLI and SDK behaviour as fallback
context for understanding handles; do not replace an available MCP upload/history tool
with a separate path unless the user explicitly approves it.

## Media Manifest

Write uploads to `generated/media_manifest.md`:

| Local path | Absolute path | Role hints | MCP media handle | Handle type | Uploaded at | Notes |
|------------|---------------|------------|------------------|-------------|-------------|-------|
| shots/S01_SH001/start.png | /abs/project/shots/S01_SH001/start.png | start_image | uuid-or-url | uuid/url/history_id | 2026-05-05T12:00:00Z | |

Use this file as a cache. If a local path already has a media handle and the file has
not changed, reuse the handle.

## Upload Procedure

1. Resolve each local path relative to the project root.
2. Confirm the file exists and is readable.
3. Inspect the live MCP schema for accepted media input forms: local file, upload
   handle, CDN URL, generation-history ID, or previous-output selector.
4. Upload or register start and end frames first.
5. Upload character, location, prop, and recurring visual element refs only when the chosen
   model accepts `image` role references for the job.
6. Upload style references last.
7. Record the handle immediately.

If the live MCP route only accepts public image URLs, use the MCP's own upload/history
tool or an approved Higgsfield upload helper to create those URLs. Stop if no approved
path exists from local frame files to accepted MCP media inputs.

## Generation Log

Write `generated/generation_log.md`:

| Shot ID | Sub-clip | Take | Model | Job ID | Status | Output URL | Local file | Prompt hash | Notes |
|---------|----------|------|-------|--------|--------|------------|------------|-------------|-------|

Append a row as soon as the Higgsfield MCP video tool returns a job ID, request ID, or
job-set ID. Update the row while polling.

## Resume Rules

- If a row is `completed` and `Local file` exists, skip it.
- If a row has a job ID but no terminal status, poll before resubmitting.
- If a row is `failed`, create the next take unless the user asks to retry the same job.
- Never overwrite an existing take; write `v2`, `v3`, etc.
