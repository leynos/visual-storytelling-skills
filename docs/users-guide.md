# Users' guide

This guide describes the architecture and workflows of the
visual-storytelling-skills toolkit. It covers the shot-specifier
execution sequence, the relationships between all skills and their
supporting components, and the reference-image generation pipeline
inside the scene-inventory-extractor-v2.

______________________________________________________________________

## Shot-specifier workflow

The sequence diagram below traces a single run of the `shot-specifier`
skill. The skill loads all prerequisite assets from the file system,
works through shot decomposition, frame-role assignment, and directorial
direction, then enters a per-shot loop. Inside the loop it checks for
missing references (generating and cataloguing any that are absent),
generates storyboard frames via `nanobanana`, runs consistency checks,
assembles the video prompt, and submits the generation job to the chosen
video model. The generation log is updated after every clip.

The purple band covers the three preparatory phases; the blue band
covers storyboard generation; the green band covers model routing,
prompt assembly, and video submission.

```mermaid
sequenceDiagram
  actor User
  participant Shot_specifier as shot_specifier
  participant Nanobanana as nanobanana_skill
  participant Video_models as video_models_seedance_kling
  participant FS as file_system_assets

  User->>Shot_specifier: Provide scene_inventory
  Shot_specifier->>FS: Load scene_inventory, prompt_keywords, reference_images, video_role_manifest

  rect rgb(230,230,250)
    Shot_specifier->>Shot_specifier: Phase_2_Shot_Decomposition
    Shot_specifier->>Shot_specifier: Phase_3_Frame_Role_Assignment
    Shot_specifier->>Shot_specifier: Phase_4_Shot_Direction
  end

  loop For_each_shot
    Shot_specifier->>FS: Pre_generation_reference_check
    alt Missing_reference
      Shot_specifier->>FS: Generate_missing_reference
      Shot_specifier->>FS: Update_video_role_manifest
    end

    rect rgb(220,245,255)
      Shot_specifier->>Nanobanana: Request_start_end_key_frames with style_keywords + refs
      Nanobanana-->>FS: Write_start_end_key_frames
    end

    Shot_specifier->>FS: Run_storyboard_consistency_checks (character, location, prop, cross_shot_prop_identity)

    rect rgb(240,255,220)
      Shot_specifier->>Shot_specifier: Consult_model_routing_guidance
      Shot_specifier->>FS: Assemble_video_prompt_for_shot using prompt_keyword_library
      Shot_specifier->>Video_models: Submit_generation_job with start_image, end_image, refs, prompt, model_choice
      Video_models-->>FS: Write_generated_clip
      Video_models-->>FS: Append_generation_log_entry
    end
  end
```

*Figure 1 — Shot-specifier execution sequence. The skill processes one
shot at a time. Missing references are resolved before storyboard frames
are generated. Video generation does not begin until consistency checks
pass.*

______________________________________________________________________

## Skill architecture

The class diagram below shows every skill, script, and reference
document in the toolkit and the relationships between them.
`scene-inventory-extractor-v2` is the upstream skill: it produces the
prompt keyword library and scene inventory that feed `shot-specifier`,
and uses `nanobanana` to generate all reference images.
`shot-specifier` consults `model-routing-guidance` to select a video
model and uses `nanobanana` for storyboard keyframes. `phoneticize`
invokes `extract_candidates.py` for regex-based candidate detection,
consults `eleven-v3-notes` for engine constraints, and applies
`respelling-conventions` throughout. `nanobanana` is a shared
image-generation layer used by both extractor and specifier; it has no
dependency on `phoneticize`.

All nanobanana image calls in this pipeline must request
`model: gemini-3-pro-image-preview`. If that model is unavailable or cannot accept the
reference images or character-consistency images required by the current operation, the
image-generation workflow stops instead of selecting a fallback model.

```mermaid
classDiagram
  class Scene_inventory_extractor_v2 {
    +Phase_1_Source_analysis()
    +Phase_2_Creative_pillars()
    +Phase_2_4_Prompt_keyword_library()
    +Phase_6_Scene_inventory()
    +Phase_8_Continuity_inventory()
    +Phase_9_Shot_lists_with_duration_budget()
    +Phase_11_Reference_image_generation()
    +Phase_11_5_Video_role_manifest()
    +Phase_12_Shot_frame_generation()
    +Phase_13_Consistency_verification()
    +Phase_14_Video_prompt_assembly()
  }

  class Shot_specifier {
    +Phase_1_Input_audit()
    +Phase_2_Shot_decomposition()
    +Phase_3_Frame_role_assignment()
    +Phase_4_Shot_direction()
    +Phase_5_Storyboard_generation()
    +Phase_6_Storyboard_consistency_check()
    +Phase_7_Video_prompt_assembly()
    +Phase_8_Asset_pipeline()
    -use_model_routing_guidance()
    -use_asset_pipeline_conventions()
  }

  class Phoneticize {
    +Phase_1_Scan_and_extract_candidates()
    +Phase_2_Suggest_respellings()
    +Phase_3_Render_TTS_samples()
    +Phase_4_Iterate_with_user()
    +Phase_5_Emit_phoneticized_script()
    -load_detection_heuristics()
    -apply_respelling_conventions()
    -respect_eleven_v3_constraints()
  }

  class Extract_candidates_py {
    +main(argv)
    +find_candidates(text,allowlist)
    +lemmatise(token)
    +context_fragment(text,position,token_length)
    +is_sentence_initial(text,position)
    +appears_lowercase_elsewhere(token,text)
    -COMMON_ALL_CAPS
    -COMMON_TITLE_CASE
  }

  class Nanobanana_skill {
    +generate_image(prompt,model,aspect_ratio,output_path)
    +edit_image(prompt,input_path,model,output_path)
    +character_consistency(prompt,character_ref,model,output_path)
    +multi_image_fusion(prompt,refs,model,output_path)
    +select_prompt_framework()
  }

  class Model_routing_guidance {
    +select_model_for_shot_type()
    +document_routing_rationale()
    +log_online_evidence()
    +plan_further_research()
  }

  class Prompt_keyword_library_doc {
    +define_global_style_phrase()
    +define_location_vocabulary()
    +define_lighting_condition_vocabulary()
    +define_negative_constraints()
    +define_POV_overrides()
  }

  class Eleven_v3_notes {
    +document_phoneme_tag_limits()
    +document_alias_dictionary_format()
    +document_pause_and_prosody_rules()
  }

  class Respelling_conventions {
    +define_respelling_style_rules()
    +document_possessive_format()
    +archive_IPA_examples()
  }

  Scene_inventory_extractor_v2 --> Prompt_keyword_library_doc : produces_and_uses
  Scene_inventory_extractor_v2 --> Shot_specifier : downstream_skill_input
  Scene_inventory_extractor_v2 --> Nanobanana_skill : uses_for_reference_images

  Shot_specifier --> Nanobanana_skill : uses_for_storyboards
  Shot_specifier --> Model_routing_guidance : consults

  Phoneticize --> Extract_candidates_py : invokes

  Phoneticize --> Eleven_v3_notes : consults
  Phoneticize --> Respelling_conventions : applies
```

*Figure 2 — Skill and component relationships. Arrows show dependency
direction: an arrow from A to B means A depends on or produces input for
B. `nanobanana` is a shared image-generation layer; it does not depend
on any other skill. `phoneticize` is independent of the
image-generation pipeline.*

______________________________________________________________________

## Reference image generation pipeline

The flowchart below shows Phase 11 of `scene-inventory-extractor-v2` in
detail, together with the consistency verification loop that follows in
Phases 12 and 13. Prop references are classified in Phase 6 as either
required-before-Phase-12 (props that appear in video frames and must be
locked before any shot-frame generation begins) or incidental (props
that can be generated after location references without blocking shot
generation). The flowchart enforces that all required-before-Phase-12
prop primaries are locked before location references are generated.
Phase 12 performs a per-shot reference check; if anything is missing,
control returns to Phase 11. Phase 13 checks both individual prop
consistency against the primary reference and cross-shot prop identity
across all frames.

```mermaid
flowchart TD
  A[Phase 6: Scene Inventory
  classify prop reference priority
  required-before-Phase-12 vs incidental] --> B[Phase 11 start
  Reference image generation]

  B --> C[Generate style anchors
  11.1 Style Anchor]
  C --> D[Generate all character primary and additional refs
  11.2 Character References]

  D --> E[Generate required-before-Phase-12 prop refs
  11.3 Prop References
  primary + variants]
  E --> F{All required-before-Phase-12
  prop primary refs locked?}
  F -- no --> E
  F -- yes --> G[Generate location refs
  11.4 Location Scouting References]
  G --> H[Generate incidental prop refs
  primary + variants]

  H --> I[Generate reference image manifest]
  I --> J[Generate video role manifest
  11.5 Video Role Manifest
  assign start_image,end_image,image,video,audio roles]

  J --> K[Phase 12: Shot-frame generation
  Pre-generation check per shot]

  K --> L{For this shot:
  refs for all named characters,
  required props,
  correct location variant exist?}
  L -- no --> B
  L -- yes --> M[Generate start, key, end frames
  using prompt keyword library
  and locked refs]

  M --> N[Phase 13: Consistency verification]

  N --> O[Check prop consistency
  vs primary prop ref]
  N --> P[Check cross-shot prop identity
  view all frames with each named prop]

  O --> Q{Prop mismatch vs primary ref?}
  Q -- yes --> R[Regenerate offending frames
  using locked prop primary ref]
  Q -- no --> S[Prop consistent]

  P --> T{Prop looks like different object
  across shots?}
  T -- yes --> R
  T -- no --> U[Cross-shot prop identity confirmed]
```

*Figure 3 — Reference image generation and consistency verification
pipeline (Phases 6, 11, 12, and 13 of `scene-inventory-extractor-v2`).
Required-before-Phase-12 props must be fully locked before location
reference generation begins. Phase 12 loops back to Phase 11 if any
reference is missing. Phase 13 enforces both per-shot prop consistency
and cross-shot prop identity.*
