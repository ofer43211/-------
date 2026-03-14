# CLAUDE.md

## Project Overview

This is a **Unified Projects Monorepo** that consolidates 23 AI and infrastructure projects into a single organized workspace. It uses npm workspaces, Turborepo, and Lerna for orchestration. Currently 10 public projects are cloned; 13 private projects require GitHub authentication.

## Tech Stack

- **Runtime**: Node.js 18+, npm 9+
- **Monorepo orchestration**: npm workspaces + Turborepo (v1.11.0) + Lerna (v8.0.0)
- **Language**: JavaScript/TypeScript (individual sub-projects vary)
- **Sub-projects**: Mixed stacks (React, Next.js, Firebase, Python, Go, etc.)

## Repository Structure

```
unified-projects-monorepo/
├── package.json              # Root workspace config
├── turbo.json                # Turborepo build pipeline
├── packages/
│   ├── rotem/                # RoTEM AI System (7 projects, 1 public)
│   ├── gemini/               # Gemini/Biju AI (3 projects, 1 public)
│   ├── ai-platforms/         # Enterprise AI Platforms (6 projects, 2 public)
│   ├── tools/                # Dev Tools & SDKs (3 projects, all public)
│   └── infrastructure/       # Infrastructure Services (4 projects, 3 public)
├── tools/
│   ├── consolidate-projects.js   # Clones/updates all sub-projects from GitHub
│   └── check-projects.js         # Reports which projects are present locally
└── docs/
    ├── CONSOLIDATION.md      # How consolidation works
    ├── PRIVATE_REPOS.md      # Auth guide for private repos
    └── SHARED_PACKAGES.md    # Guide for creating shared packages
```

## Key Commands

| Command | Purpose |
|---|---|
| `npm run bootstrap` | Initial setup: install deps + clone all sub-projects |
| `npm run consolidate` | Clone/update all 23 projects from GitHub |
| `npm run status` | Check which projects are present locally |
| `npm run build:all` | Build all workspace projects (via Turbo) |
| `npm run test:all` | Run tests across all workspaces |
| `npm run clean` | Remove all node_modules directories |

## Key Entry Points

- **`tools/consolidate-projects.js`** — Main orchestrator. Defines all 23 projects with their GitHub URLs and category mappings. Edit this file to add/remove projects.
- **`tools/check-projects.js`** — Status checker. Reports which projects exist locally vs. missing.
- **`package.json`** — Root workspace definition. The `workspaces` array determines which directories are npm workspace members.
- **`turbo.json`** — Build pipeline. Defines task dependencies: `build` → `test` → `lint`, with caching config.

## Build Pipeline (Turbo)

- **build**: Depends on upstream builds (`^build`). Outputs: `dist/`, `build/`, `.next/`
- **test**: Depends on `build`. Outputs: `coverage/`
- **lint**: No caching
- **dev**: No caching, persistent (for dev servers)
- **clean**: No caching

## Development Conventions

### Working on a sub-project
```bash
cd packages/<category>/<project>
npm install
npm run dev
```

### Adding a new project
1. Edit `tools/consolidate-projects.js` — add entry to the appropriate category array
2. Run `npm run consolidate`

### Shared packages
- Place in `packages/shared/` (not yet in workspace globs — add `"packages/shared/*"` to root `package.json` workspaces if needed)
- Use scoped names: `@unified/utils`, `@unified/types`, etc.
- Reference with `"workspace:*"` in dependent package.json files

### Git strategy
- Each sub-project under `packages/` retains its own `.git` directory and full commit history
- Sub-projects can still push/pull independently from their original repos
- The monorepo provides umbrella organization and shared tooling

## Important Notes for AI Assistants

- **Do not run `npm run consolidate`** without user approval — it clones repos from GitHub and takes time.
- **Sub-project directories may not exist** if consolidation hasn't been run or auth is missing. Check with `npm run status` first.
- **Each sub-project is independent** with its own package.json, build config, and test setup. Read the sub-project's own README/config before making changes.
- **The root package.json is private** — this monorepo is not published to npm.
- **13 private repos require GitHub auth** — see `docs/PRIVATE_REPOS.md`. Don't assume all projects are available.
- **Turbo caches builds** — if you need a fresh build, use `npm run clean` first.
- When making cross-project changes, commit them together for atomicity.
