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

## Manifest Requirement

The manifest must record sub-clips:

| Shot ID | Sub-clip | Start | End | Duration | Strategy |
|---------|----------|-------|-----|----------|----------|
| S04_SH004 | A | start.png | key01.png | 4s | split_at_keyframe |
| S04_SH004 | B | key01.png | end.png | 4s | split_at_keyframe |
