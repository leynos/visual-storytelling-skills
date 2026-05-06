# media-project

Package generated visual storytelling clips into editor project files.

## OpenShot packaging

Run the OpenShot packager after `video-generator` has written
`generated/assembly_order.md`, `generated/generation_log.md`, and all selected
local clips:

```bash
uv run media-project package-openshot \
  --project-root /path/to/story-project \
  --output generated/media-project/project.osp \
  --sidecar generated/media-project/media-project.json
```

The command writes deterministic JSON. It fails when a selected clip is
missing, a take has not reached a completed status, a required take has not
been accepted for review, a duration is absent, or the output already exists
without `--force`.
