#!/usr/bin/env bash

for a in codex claude; do for i in skills/*; do rm -rvf ~/".${a}/skills/${i##*/}"; cp -vR "${i}" ~/".${a}/skills/."; done; done
