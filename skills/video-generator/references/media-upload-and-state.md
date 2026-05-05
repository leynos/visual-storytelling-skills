# Media Upload and State Tracking

Higgsfield Model Context Protocol (MCP) video generation cannot consume repo-relative
paths directly unless the connected tool explicitly supports local file uploads. The
prompt manifest uses local paths for reviewability, so generation must convert those
paths into whatever media handle the connected Higgsfield MCP accepts: uploaded media
UUID, CDN URL, generation history ID, or a tool-specific file input.

Canonical shot-specifier frame paths are:

```text
shots/{shot_id}/start.png
shots/{shot_id}/end.png
shots/{shot_id}/key{NN}.png
```

Scene-inventory legacy paths such as `scene-pack/shots/shot_{shot_id}_start.png` are
valid only when the manifest names them explicitly. Do not infer legacy paths. Manifest
paths may be project-root-relative or absolute; resolve and verify the exact manifest
value before upload.

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
3. Confirm every continuity-critical file named by `required_refs`, the prompt
   `Reference Audit`, or the storyboard consistency report is either present in this
   upload set or intentionally excluded with a blocker. Actioning the consistency pass
   is mandatory; do not treat it as background information.
4. Inspect the live MCP schema for accepted media input forms: local file, upload
   handle, CDN URL, generation-history ID, or previous-output selector.
5. Upload or register start and end frames first.
6. Upload character, location, prop, and recurring visual element refs only when the chosen
   model accepts `image` role references for the job.
7. Upload style references last.
8. Record the handle immediately.

If the live MCP route only accepts public image URLs, use the MCP's own upload/history
tool or an approved Higgsfield upload helper to create those URLs. Stop if no approved
path exists from local frame files to accepted MCP media inputs.

## Generation Log

Write `generated/generation_log.md`:

| Shot ID | Sub-clip | Take | Model | Job ID | Status | Output URL | Local file | File size | Actual resolution | Review | Prompt hash | Notes |
|---------|----------|------|-------|--------|--------|------------|------------|-----------|-------------------|--------|-------------|-------|

Append a row as soon as the Higgsfield MCP video tool returns a job ID, request ID, or
job-set ID. Update the row while polling.

After download, fill in `File size` and `Actual resolution` from the local file. These
fields are capacity-planning data, not cosmetic metadata: large model-to-model bitrate
variance can change storage and transfer costs across a full production.

Use empirical baselines as review triggers:

- compare each file against prior successful takes with the same model, duration, and
  resolution parameter;
- if no same-class baseline exists, record the new value as provisional;
- if the file is below 50% of the lowest comparable baseline, or above 2x the current
  median without a known reason, mark `Review=required` and inspect for truncation,
  missing audio, unexpectedly low bitrate, or wrong resolution.

Known provisional baselines from S01:

| Model | Duration | Observed file size | Notes |
|-------|----------|--------------------|-------|
| `seedance_2_0` | 6 s | about 4.3 MB | Treat smaller files as suspicious until more samples exist |
| `kling3_0` | 8 s | about 21 MB | One 16:9 landscape sample; bitrate variance may be high |

## Review Gates

Each manifest row carries `review_gate`:

- `required` for character-centric, continuity-critical, dialogue, product, prop, UI, or
  expensive hero shots;
- `optional` for low-risk v1 landscape or atmosphere shots.

For required gates, download the take, update the log, then pause automatic progression
until the take is reviewed against the shot spec, storyboard frames, continuity
constraints, and audio preferences. Record `accepted`, `retake`, or `blocked` in the
`Review` column.

## Submission Strategy

Record the batching strategy in `generated/generation_log.md` or
`generated/submission_plan.md` before submitting large runs.

- Mixed run: submit one Seedance job early if any Seedance shots exist, then fill the
  remaining plan-level concurrency with Kling or other non-Seedance jobs. When the
  Seedance job reaches a terminal state, submit the next Seedance job.
- Seedance-heavy run: declare `queue_strategy=seedance_serial` and submit Seedance shots
  in assembly order unless a later shot is a lower-risk atmosphere insert that can fill
  idle time. Do not flood the queue with many Seedance jobs unless the live surface
  proves parallel Seedance execution and the generation log records that evidence.
- Kling-heavy run: submit up to the plan-level video concurrency limit observed in the
  live account, but still log every returned job ID immediately.
- Do not treat long `queued` status as failure by itself. Treat an unchanging
  `in_progress` state beyond the provider's normal range as a manual review item.

## Count and Multi-Take Handling

`count` is schema-gated. The public Higgsfield pages confirm plan-level parallel video
limits but do not publish a per-call MCP `count` contract.

- Default `count=1`.
- Use `count=2` for review-gated hero shots, difficult identity interpolation, or shots
  with known model instability when credits and queue time allow.
- Avoid `count>1` on Seedance-heavy runs unless the shot is critical; it multiplies
  serial queue pressure.
- If the live MCP schema exposes `count`, one returned job set must expand to distinct
  take rows: `v1`, `v2`, etc.
- If `count` is not exposed, submit separate take jobs only when the manifest requests
  multiple takes and the operator accepts the added cost.

## Resume Rules

- If a row is `completed` and `Local file` exists, skip it.
- If a row has a job ID but no terminal status, poll before resubmitting.
- If a row is `failed`, create the next take unless the user asks to retry the same job.
- If a row is `completed` but `Review` is `retake`, create the next take after fixing the
  root cause.
- Never overwrite an existing take; write `v2`, `v3`, etc.
