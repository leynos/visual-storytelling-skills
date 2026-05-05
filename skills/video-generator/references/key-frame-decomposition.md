# Key-Frame Decomposition

Higgsfield generation jobs in this workflow accept `start_image` and `end_image` roles.
They do not accept mid-clip key-frame anchors. A shot with key frames must be decomposed
before video generation.

## Strategy Values

| Strategy | Use when |
|----------|----------|
| `single_clip` | No key frames; start and end only |
| `split_at_keyframe` | Key frame represents a required intermediate state |
| `merge_keyframe_motion` | Key frame is advisory and the model minimum duration would make splitting worse |

## Split Algorithm

For a shot with start, key frames, and end:

1. Sort anchors by time: start at 0, key frames by timestamp, end at shot duration.
2. Create sub-clips between adjacent anchors: start -> key01, key01 -> key02, keyNN ->
   end.
3. Each sub-clip receives one `start_image` and one `end_image`.
4. Validate each sub-clip duration against the selected model.
5. If a sub-clip is below the model minimum, choose one:
   - Extend the sub-clip to the model minimum and reduce the neighbour if still valid.
   - Merge the key-frame motion into the nearest valid sub-clip and mark
     `generation_strategy: merge_keyframe_motion`.
   - Change model only if the new model is already approved by routing guidance.

## Example

`S04_SH004`, 6 s, key at 2 s:

| Sub-clip | Anchors | Natural duration | Seedance-valid duration |
|----------|---------|------------------|-------------------------|
| A | start -> key01 | 2 s | 4 s or merge |
| B | key01 -> end | 4 s | 4 s |

Because `seedance_2_0` has a 4 s minimum in this workflow, either extend A to 4 s and
adjust B if the action still works, or mark the shot `merge_keyframe_motion` and encode
the key-frame state in the generation prompt.

## Worked Merge Example

Use `merge_keyframe_motion` when the key frame is useful timing guidance but splitting
would produce invalid or awkward sub-clips.

Example shot:

```text
Shot: S05_SH003
Duration: 8 s
Start: shots/S05_SH003/start.png
Key 01 at 3 s: shots/S05_SH003/key01.png
End: shots/S05_SH003/end.png
Reason to merge: the key frame is a lighting/action beat, not a required separate anchor.
```

Structured intent:

- start frame: Maeve faces a dark monitoring console;
- key frame at 3 s: red warning light reflects across the wall and her cheek;
- end frame: Maeve turns partly away from the console, hand still on the switch.

Prompt language for a single unsplit clip:

```text
From the start frame, Maeve holds her gaze on the dark monitoring console, hand already
resting on the switch. Over the first third of the clip the console remains dim and her
body stays still. Around the middle of the clip, a red warning pulse rises from the
console and sweeps across the wall and her cheek, matching the advisory key-frame state.
By the final seconds she turns partly away from the console while keeping her hand on the
switch, resolving exactly into the supplied end frame. Preserve the console layout,
switch position, wardrobe, and lighting direction throughout. No narration.
```

Upload only the start and end images for the generation job. Keep the key frame path in
the manifest and notes as the advisory state that has been merged into the prompt.

## Manifest Requirement

The manifest must record sub-clips:

| Shot ID | Sub-clip | Start | End | Duration | Strategy |
|---------|----------|-------|-----|----------|----------|
| S04_SH004 | A | start.png | key01.png | 4s | split_at_keyframe |
| S04_SH004 | B | key01.png | end.png | 4s | split_at_keyframe |

For `merge_keyframe_motion`, record the key frame without using it as an upload anchor:

| Shot ID | Sub-clip | Start | End | Duration | Strategy | Advisory key |
|---------|----------|-------|-----|----------|----------|--------------|
| S05_SH003 | A | start.png | end.png | 8s | merge_keyframe_motion | key01.png |
