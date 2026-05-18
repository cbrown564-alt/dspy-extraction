---
name: windows-portability
description: Use when preparing this repo for Windows development or reviewing code, scripts, paths, commands, environment loading, subprocesses, model adapters, or docs for macOS/Linux assumptions that may break on Windows.
---

# Windows Portability

Use this skill before porting the project to Windows or when editing setup, scripts, paths, model execution, or docs that should work on both macOS and Windows.

## Workflow

1. Identify the files and workflow that must run on Windows.
2. Search for platform assumptions:
   - hardcoded `/Users/...` or POSIX-only paths
   - shell-specific commands or `zsh` assumptions
   - path parsing with `/` instead of `pathlib.Path`
   - executable names that differ on Windows
   - environment-variable loading assumptions
   - subprocess calls that require POSIX shell behavior
   - line ending or encoding assumptions
3. Prefer Python entry points and `pathlib` over shell-specific glue for portable workflows.
4. Keep model/provider settings in config; do not assume macOS local model availability when Windows is the target.
5. Document Windows-specific setup only when it differs materially from macOS.
6. Add or update tests for path handling and config loading where practical.

## Portability Checks

- Can commands run through `uv run ...` without relying on shell aliases?
- Are data paths relative to repo roots or configured paths rather than absolute local paths?
- Are generated artifacts written with explicit UTF-8 encoding?
- Are scripts robust to spaces in paths, especially dataset folders such as `data/ExECTv2 (2025)`?
- Are long-running model calls using configurable timeouts?
- Is Ollama or local-model setup documented as provider-specific rather than assumed?

## Completion Criteria

Before finishing, summarize:

- Windows-sensitive workflow reviewed
- macOS/POSIX assumptions found
- code or docs changed
- validation run or not run
- remaining Windows risks
