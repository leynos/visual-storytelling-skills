#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

for a in codex claude; do
  target_root="${HOME}/.${a}/skills"
  mkdir -p "${target_root}"

  for i in skills/*; do
    skill_name="${i##*/}"
    staging_root="$(mktemp -d "${target_root}/.${skill_name}.staging.XXXXXX")"
    staged_skill="${staging_root}/${skill_name}"
    old_skill="${target_root}/.${skill_name}.old"
    target_skill="${target_root}/${skill_name}"

    cp -vR "${i}" "${staged_skill}"
    rm -rf "${old_skill}"

    had_target=0
    if [ -e "${target_skill}" ]; then
      had_target=1
      mv "${target_skill}" "${old_skill}"
    fi

    if ! mv "${staged_skill}" "${target_skill}"; then
      if [ "${had_target}" -eq 1 ]; then
        mv "${old_skill}" "${target_skill}"
      fi
      rm -rf "${staging_root}"
      exit 1
    fi

    rm -rf "${old_skill}" "${staging_root}"
  done
done
