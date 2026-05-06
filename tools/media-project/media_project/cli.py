"""Command-line interface for media-project."""

from __future__ import annotations

import pathlib

from cyclopts import App

from media_project.openshot_project import (
    InputValidationError,
    OutputExistsError,
    PackageRequest,
    ProjectSettings,
    package_openshot_project,
)

app = App(help="Package generated visual storytelling media into editor projects.")


@app.command(name="package-openshot")
def package_openshot(
    *,
    project_root: pathlib.Path,
    assembly_order: pathlib.Path = pathlib.Path("generated/assembly_order.md"),
    generation_log: pathlib.Path = pathlib.Path("generated/generation_log.md"),
    manifest: pathlib.Path | None = None,
    output: pathlib.Path = pathlib.Path("generated/media-project/project.osp"),
    sidecar: pathlib.Path = pathlib.Path("generated/media-project/media-project.json"),
    project_name: str = "visual-storytelling-project",
    force: bool = False,
    width: int = 1920,
    height: int = 1080,
    fps_num: int = 24,
    fps_den: int = 1,
    sample_rate: int = 44100,
    channels: int = 2,
    channel_layout: int = 3,
) -> None:
    """Create an OpenShot project JSON file from generated media metadata."""
    request = PackageRequest(
        project_root=project_root,
        assembly_order=assembly_order,
        generation_log=generation_log,
        output=project_root / output,
        sidecar=project_root / sidecar,
        source_manifest=manifest,
        project_name=project_name,
        force=force,
        settings=ProjectSettings(
            width=width,
            height=height,
            fps_num=fps_num,
            fps_den=fps_den,
            sample_rate=sample_rate,
            channels=channels,
            channel_layout=channel_layout,
        ),
    )
    try:
        package_openshot_project(request)
    except (InputValidationError, OutputExistsError) as exc:
        raise SystemExit(str(exc)) from exc


def main() -> None:
    """Run the media-project command-line application."""
    app()


if __name__ == "__main__":
    main()
