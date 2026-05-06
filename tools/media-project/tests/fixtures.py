"""Reusable media-project test fixture builders."""

from __future__ import annotations

import typing as typ

if typ.TYPE_CHECKING:
    import pathlib


def create_story_project(root: pathlib.Path) -> None:
    """Create a small generated-media project fixture."""
    (root / "generated" / "clips").mkdir(parents=True)
    for filename in (
        "s01_sh001_take2.mp4",
        "s01_sh002_take1.mp4",
        "s01_sh003_take3.mp4",
    ):
        (root / "generated" / "clips" / filename).write_bytes(b"fake mp4")

    (root / "generated" / "assembly_order.md").write_text(
        _markdown_table(
            "Assembly Order",
            (
                "Order",
                "Shot ID",
                "Sub-clip",
                "Selected clip",
                "Boundary after",
                "Notes",
            ),
            (
                (
                    "1",
                    "S01_SH001",
                    "A",
                    "generated/clips/s01_sh001_take2.mp4",
                    "cut",
                    "Hold first look.",
                ),
                (
                    "2",
                    "S01_SH002",
                    "A",
                    "generated/clips/s01_sh002_take1.mp4",
                    "dissolve",
                    "Match movement.",
                ),
                (
                    "3",
                    "S01_SH003",
                    "B",
                    "generated/clips/s01_sh003_take3.mp4",
                    "cut",
                    "End on object.",
                ),
            ),
        ),
        encoding="utf-8",
    )
    (root / "generated" / "generation_log.md").write_text(
        _generation_log_markdown(),
        encoding="utf-8",
    )


def _generation_log_markdown() -> str:
    return _markdown_table(
        "Generation Log",
        (
            "Shot ID",
            "Sub-clip",
            "Take",
            "Model",
            "Job ID",
            "Status",
            "Output URL",
            "Local file",
            "File size",
            "Actual resolution",
            "Review",
            "Prompt hash",
            "Notes",
            "Duration seconds",
            "Transition type",
            "Transition duration",
            "Mute generated audio",
            "Forced generated audio",
            "Scene ID",
            "Prompt file",
            "Continuity flags",
        ),
        (
            _generation_row(
                {
                    "shot_id": "S01_SH001",
                    "take": "take-2",
                    "model": "kling-3",
                    "job_id": "job-001",
                    "status": "completed",
                    "review": "accepted",
                    "prompt_hash": "hash-001",
                    "notes": "Clean take.",
                    "duration": "2.5",
                    "transition": "cut",
                    "transition_duration": "0",
                    "mute_audio": "true",
                    "forced_audio": "true",
                    "continuity_flags": "eyeline, wardrobe",
                },
            ),
            _generation_row(
                {
                    "shot_id": "S01_SH002",
                    "take": "take-1",
                    "model": "seedance-2",
                    "job_id": "job-002",
                    "status": "completed",
                    "review": "approved",
                    "prompt_hash": "hash-002",
                    "notes": "Best motion.",
                    "duration": "3.25",
                    "transition": "dissolve",
                    "transition_duration": "0.5",
                    "mute_audio": "false",
                    "forced_audio": "false",
                    "continuity_flags": "eyeline",
                },
            ),
            _generation_row(
                {
                    "shot_id": "S01_SH003",
                    "subclip": "B",
                    "take": "take-3",
                    "model": "kling-3",
                    "job_id": "job-003",
                    "status": "succeeded",
                    "review": "final",
                    "prompt_hash": "hash-003",
                    "notes": "Locked.",
                    "duration": "1.75",
                    "transition": "cut",
                    "transition_duration": "0",
                    "mute_audio": "false",
                    "forced_audio": "false",
                    "continuity_flags": "prop reset",
                },
            ),
        ),
    )


def _generation_row(row: dict[str, str]) -> tuple[str, ...]:
    shot_id = row["shot_id"]
    take = row["take"]
    job_id = row["job_id"]
    return (
        shot_id,
        row.get("subclip", "A"),
        take,
        row["model"],
        job_id,
        row["status"],
        f"https://example.test/{job_id[-1]}",
        f"generated/clips/{shot_id.lower()}_take{take[-1]}.mp4",
        "10 KiB",
        "1344x768",
        row["review"],
        row["prompt_hash"],
        row["notes"],
        row["duration"],
        row["transition"],
        row["transition_duration"],
        row["mute_audio"],
        row["forced_audio"],
        "S01",
        f"prompts/{shot_id}.md",
        row["continuity_flags"],
    )


def _markdown_table(
    title: str,
    headings: tuple[str, ...],
    rows: tuple[tuple[str, ...], ...],
) -> str:
    header = "| " + " | ".join(headings) + " |"
    separator = "| " + " | ".join("---" for _heading in headings) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
    return f"# {title}\n\n{header}\n{separator}\n{body}\n"
