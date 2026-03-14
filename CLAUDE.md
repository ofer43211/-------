# CLAUDE.md

## Project Overview

This is a **Unified Projects Monorepo** that consolidates 23 AI and infrastructure projects into a single organized workspace. It uses npm workspaces, Turborepo, and Lerna for orchestration. Currently 10 public projects are cloned; 13 private projects require GitHub authentication.

## Tech Stack

- **Runtime**: Node.js 18+, npm 9+
- **Monorepo orchestration**: npm workspaces + Turborepo (v1.11.0) + Lerna (v8.0.0)
- **Testing**: Jest 29 + ts-jest (shared preset in `jest.preset.js`)
- **CI/CD**: GitHub Actions (build/test matrix on Node 18 & 20, lint, project status checks)
- **Dependency management**: Dependabot (weekly, per-project, with auto-merge for patch/minor)
- **Language**: JavaScript/TypeScript (individual sub-projects vary)
- **Sub-projects**: Mixed stacks (React, Next.js, Firebase, Python, Go, etc.)

## Repository Structure

```
unified-projects-monorepo/
├── package.json                # Root workspace config
├── turbo.json                  # Turborepo build pipeline
├── jest.config.js              # Root Jest config (multi-project runner)
├── jest.preset.js              # Shared Jest preset for sub-projects
├── CLAUDE.md                   # This file
├── .github/
│   ├── dependabot.yml          # Automated dependency updates config
│   └── workflows/
│       ├── ci.yml              # Main CI pipeline (build, test, lint)
│       └── dependabot-auto-merge.yml  # Auto-merge patch/minor dep PRs
├── packages/
│   ├── shared/                 # Shared libraries (workspace: @unified/*)
│   │   ├── ui/                 # @unified/ui — React component library (Button, Card, StatusBadge)
│   │   └── utils/              # @unified/utils — Logger, validators, formatters
│   ├── rotem/                  # RoTEM AI System (7 projects, 1 public)
│   ├── gemini/                 # Gemini/Biju AI (3 projects, 1 public)
│   ├── ai-platforms/           # Enterprise AI Platforms (6 projects, 2 public)
│   ├── tools/                  # Dev Tools & SDKs (3 projects, all public)
│   └── infrastructure/         # Infrastructure Services (4 projects, 3 public)
├── tools/
│   ├── consolidate-projects.js # Clones/updates all sub-projects from GitHub
│   ├── check-projects.js       # Reports which projects are present locally
│   ├── generate-docs.js        # Generates docs/PROJECT_CATALOG.md from sub-projects
│   └── link-projects.js        # Symlinks shared packages into sub-projects for dev
└── docs/
    ├── CONSOLIDATION.md        # How consolidation works
    ├── PRIVATE_REPOS.md        # Auth guide for private repos
    ├── SHARED_PACKAGES.md      # Guide for creating shared @unified/* packages
    └── PROJECT_CATALOG.md      # Auto-generated project catalog (via generate-docs.js)
```

## Key Commands

| Command | Purpose |
|---|---|
| `npm run bootstrap` | Initial setup: install deps + clone all sub-projects |
| `npm run consolidate` | Clone/update all 23 projects from GitHub |
| `npm run status` | Check which projects are present locally |
| `npm run build:all` | Build all workspace projects (via Turbo) |
| `npm test` | Run Jest across all projects (root multi-project config) |
| `npm run test:all` | Run tests across all workspaces via npm |
| `npm run link` | Symlink shared packages into all sub-projects |
| `npm run link:status` | Show which sub-projects have shared package links |
| `npm run link:clean` | Remove all inter-project symlinks |
| `npm run docs:generate` | Regenerate `docs/PROJECT_CATALOG.md` from sub-project metadata |
| `npm run clean` | Remove all node_modules directories |

## Key Entry Points

- **`tools/consolidate-projects.js`** — Main orchestrator. Defines all 23 projects with their GitHub URLs and category mappings. Edit this file to add/remove projects.
- **`tools/check-projects.js`** — Status checker. Reports which projects exist locally vs. missing.
- **`tools/generate-docs.js`** — Documentation generator. Scans sub-projects for package.json, README, and language indicators, then writes `docs/PROJECT_CATALOG.md`.
- **`tools/link-projects.js`** — Inter-project linker. Symlinks `@unified/*` shared packages into sub-project `node_modules/` for local development.
- **`package.json`** — Root workspace definition. The `workspaces` array determines which directories are npm workspace members.
- **`turbo.json`** — Build pipeline. Defines task dependencies: `build` → `test` → `lint`, with caching config.

## Shared Packages (`packages/shared/`)

Shared libraries available to all sub-projects via `@unified/*` scope:

### @unified/ui
React component library with foundational UI components:
- `Button` — configurable variant (`primary`/`secondary`/`danger`) and size (`sm`/`md`/`lg`)
- `Card` — container with optional title
- `StatusBadge` — status indicator (`online`/`offline`/`error`/`pending`)

### @unified/utils
Common utilities:
- `Logger` — prefixed, leveled logger (info/error/warn/debug) with timestamps
- `isValidEmail()`, `isValidUrl()` — input validators
- `formatDate()`, `formatCurrency()` — output formatters

### Using shared packages in sub-projects
```json
{ "dependencies": { "@unified/utils": "workspace:*" } }
```
```typescript
import { Logger } from '@unified/utils';
import { Button } from '@unified/ui';
```

For local development without `npm install`, use `npm run link` to create symlinks.

## Testing

### Root-level config
- **`jest.config.js`** — Multi-project Jest runner that discovers `jest.config.*` files in all workspace categories.
- **`jest.preset.js`** — Shared preset (ts-jest transform, test patterns, coverage settings). Sub-projects extend this:
  ```js
  const preset = require('../../../jest.preset');
  module.exports = { ...preset, displayName: 'my-project' };
  ```

### Running tests
- `npm test` — Run all tests from root via multi-project Jest config
- `npm run test:all` — Run test script in each workspace via npm
- `cd packages/<category>/<project> && npm test` — Run tests for a single project

### Coverage
Global thresholds (50% branches/functions/lines/statements) are configured in `jest.config.js`. Per-project coverage goes to each project's `coverage/` directory.

## Build Pipeline (Turbo)

- **build**: Depends on upstream builds (`^build`). Outputs: `dist/`, `build/`, `.next/`
- **test**: Depends on `build`. Outputs: `coverage/`
- **lint**: No caching
- **dev**: No caching, persistent (for dev servers)
- **clean**: No caching

## CI/CD

### GitHub Actions (`ci.yml`)
- **Build & Test**: Runs `npx turbo run build` then `npx turbo run test` across a Node.js 18/20 matrix.
- **Lint**: Runs `npx turbo run lint` on Node.js 20.
- **Project Status Check**: Runs `check-projects.js` and `generate-docs.js` to verify project availability.
- Triggers on push/PR to `master`/`main`. Concurrent runs on the same ref are cancelled.

### Dependabot (`dependabot.yml`)
- Weekly updates every Monday for npm (root + each cloned sub-project), pip (`anthropic-sdk-python`), and GitHub Actions versions.
- PRs are labeled by category (`rotem`, `gemini`, `ai-platforms`, `tools`, `infrastructure`).
- Commit messages are prefixed: `deps(rotem)`, `deps(tools)`, `ci`, etc.

### Auto-merge (`dependabot-auto-merge.yml`)
- Patch and minor Dependabot PRs are auto-approved and squash-merged.
- Major version bumps require manual review.

## Development Conventions

### Working on a sub-project
```bash
cd packages/<category>/<project>
npm install
npm run dev
```

### Adding a new project
1. Edit `tools/consolidate-projects.js` — add entry to the appropriate category array.
2. Update `tools/check-projects.js` — add the project name to the matching category.
3. If the project is cloned (public), add a Dependabot entry in `.github/dependabot.yml`.
4. Run `npm run consolidate`.
5. Run `npm run docs:generate` to update the project catalog.

### Adding a new shared package
1. Create `packages/shared/<name>/` with `package.json` (name: `@unified/<name>`), `tsconfig.json`, and `src/`.
2. Add a `jest.config.js` that extends `jest.preset.js`.
3. Run `npm run link` to make it available to sub-projects during development.

### Inter-project linking
- `npm run link` — creates `node_modules/@unified/*` symlinks in every sub-project that has a `package.json`.
- `npm run link:status` — shows which links are active.
- `npm run link:clean` — removes all symlinks (useful before `npm install`).

### Git strategy
- Each sub-project under `packages/` retains its own `.git` directory and full commit history.
- Sub-projects can still push/pull independently from their original repos.
- The monorepo provides umbrella organization and shared tooling.

### Commit message conventions
- Dependency updates use prefixed messages: `deps`, `deps(rotem)`, `deps(tools)`, `ci`, etc.
- General changes should be descriptive and concise.

## Important Notes for AI Assistants

- **Do not run `npm run consolidate`** without user approval — it clones repos from GitHub and takes time.
- **Sub-project directories may not exist** if consolidation hasn't been run or auth is missing. Check with `npm run status` first.
- **Each sub-project is independent** with its own package.json, build config, and test setup. Read the sub-project's own README/config before making changes.
- **The root package.json is private** — this monorepo is not published to npm.
- **13 private repos require GitHub auth** — see `docs/PRIVATE_REPOS.md`. Don't assume all projects are available.
- **Turbo caches builds** — if you need a fresh build, use `npm run clean` first.
- **When adding a new sub-project**, remember to update three places: `consolidate-projects.js`, `check-projects.js`, and `.github/dependabot.yml`.
- **When adding a shared package**, create it under `packages/shared/`, extend `jest.preset.js`, and run `npm run link`.
- When making cross-project changes, commit them together for atomicity.
- After structural changes, run `npm run docs:generate` to keep the project catalog current.
