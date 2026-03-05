<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Repository Guidelines

## Project Structure & Module Organization
This repository is currently minimal (docs-first). Keep the root directory clean and introduce code in standard folders as the project grows:
- `src/` for application code and modules
- `tests/` for automated tests mirroring `src/`
- `assets/` for static resources
- `docs/` for design notes, ADRs, and operational docs
- `.github/workflows/` for CI pipelines

Until runtime code exists, keep contributor-facing files in root (for example `README.md`, `AGENTS.md`, and `LICENSE`).

## Build, Test, and Development Commands
No build toolchain is committed yet. When one is added, expose commands through `package.json` scripts or a `Makefile`, then update this guide.

Current useful commands:
- `git status` shows local modifications
- `git diff -- AGENTS.md` reviews contributor-guide edits
- `pwsh -NoProfile -Command "Get-ChildItem -Force"` lists repository contents

Expected command pattern once tooling is introduced:
- `npm run build` (or `make build`) to create production artifacts
- `npm test` (or `make test`) to run the full test suite

## Coding Style & Naming Conventions
- Use UTF-8 text and consistent line endings (prefer LF).
- Use language-idiomatic naming conventions.
- `kebab-case` for docs/assets
- `snake_case` for scripts
- `PascalCase` for classes/types where appropriate
- Keep modules single-purpose and avoid cross-layer coupling.
- Add formatter/linter configs (for example `.editorconfig` and language-specific lint rules) before scaling code volume.

## Testing Guidelines
- Mirror source layout under `tests/` (example: `src/api/client.ts` -> `tests/api/client.test.ts`).
- Name tests by behavior, not implementation details.
- Add regression tests with every bug fix.
- If coverage tooling is added, target at least 80% line coverage for changed modules.

## Commit & Pull Request Guidelines
No established commit history is present yet; adopt Conventional Commits:
- `feat: add initial parser`
- `fix: handle empty input`

Pull requests should include:
- short scope summary
- linked issue (for example `Closes #123`) when applicable
- test evidence (commands run and outcomes)
- screenshots or logs for UI/workflow-impacting changes

## Security & Configuration Tips
- Never commit secrets or tokens.
- Use `.env.example` to document required configuration keys.
- Keep machine-specific paths and credentials out of version control.
- Pin dependency versions and review licenses when adding package managers.
