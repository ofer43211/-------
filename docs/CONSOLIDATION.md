# Project Consolidation Guide

## Overview

This document explains how the project consolidation works and how to use it.

## What is Project Consolidation?

Instead of managing 23+ separate repositories, we've created a **monorepo** that contains all projects in an organized structure. This provides several benefits:

### Benefits

1. **Unified Dependency Management**: Share common dependencies across projects
2. **Simplified Development**: Work on multiple related projects simultaneously
3. **Consistent Tooling**: Use the same build, test, and lint tools everywhere
4. **Better Code Sharing**: Easy to share code between projects
5. **Atomic Commits**: Make changes across multiple projects in a single commit
6. **Simplified CI/CD**: Build and test everything together

## How It Works

### The Consolidation Script

The `tools/consolidate-projects.js` script:

1. Creates the directory structure under `packages/`
2. Clones each project from GitHub into its category folder
3. Maintains the original git history of each project
4. Creates README files for each category

### Running Consolidation

```bash
# First time setup
npm run bootstrap

# Update all projects to latest
npm run consolidate
```

### Project Organization

Projects are organized into 5 categories:

#### 1. RoTEM (`packages/rotem/`)
The RoTEM AI system components:
- **rotem_brain**: Core AI intelligence
- **RoTEM_Dashboard**: Web dashboard
- **rotem_system**: System coordination layer
- **rotem-group-chat**: Multi-agent chat system
- **rotem-ai-demo**: Demo applications
- **RoTEM_Project**: Main project structure
- **RoTEM**: Base implementation

#### 2. Gemini (`packages/gemini/`)
Gemini/Biju AI projects:
- **GeminiBiju_Unified**: Unified Gemini platform
- **gemini-cli**: Command-line interface
- **gemini-biju**: Core Biju functionality

#### 3. AI Platforms (`packages/ai-platforms/`)
Enterprise AI platforms:
- **ai-saas-platform1**: SaaS platform
- **btl-gpt-production-suite**: GPT production tools
- **AI-Empire**: Empire management system
- **AIPROJ**: AI project utilities
- **UltimateAgentConsole**: Agent management console
- **premium-business-platform**: Business platform

#### 4. Tools (`packages/tools/`)
Development tools and SDKs:
- **claude-code**: Claude development tools
- **anthropic-sdk-python**: Python SDK for Anthropic
- **github-mcp-server**: GitHub MCP server

#### 5. Infrastructure (`packages/infrastructure/`)
Infrastructure and services:
- **tailscale**: Network infrastructure
- **firebaseui-web**: Firebase authentication UI
- **TheVortex_v4**: Vortex platform
- **echosync-v6**: Synchronization service

## Working with Projects

### Working on a Single Project

```bash
# Navigate to the project
cd packages/rotem/rotem_brain

# Install its dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test
```

### Working Across Multiple Projects

```bash
# Install all dependencies
npm install

# Build all projects
npm run build:all

# Test all projects
npm run test:all
```

### Adding a New Project

1. Edit `tools/consolidate-projects.js`
2. Add your project to the appropriate category array:

```javascript
rotem: [
  // ... existing projects
  { name: 'new-rotem-component', url: 'https://github.com/user/new-rotem-component.git' }
]
```

3. Run consolidation:

```bash
npm run consolidate
```

## Development Workflow

### Making Changes

1. **Navigate to project**: `cd packages/<category>/<project>`
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes**: Edit files
4. **Test locally**: Run tests in that project
5. **Commit**: Commit to the monorepo

### Cross-Project Changes

If you need to make changes across multiple projects:

1. Make changes in each project's directory
2. Test all affected projects
3. Commit all changes together in one commit
4. This ensures atomic changes across projects

## Troubleshooting

### Project Won't Clone

If a project fails to clone:
- Check the URL in `consolidate-projects.js`
- Verify you have access to the repository
- Check your network connection

### Dependencies Not Installing

```bash
# Clean everything
npm run clean

# Re-bootstrap
npm run bootstrap
```

### Build Failures

```bash
# Build a specific project
cd packages/<category>/<project>
npm run build

# Check for errors in that project
```

## Best Practices

1. **Keep Projects Independent**: Each project should be able to build/run independently
2. **Share Common Code**: Put shared utilities in a dedicated package
3. **Consistent Scripts**: Use the same script names across projects (dev, build, test)
4. **Document Dependencies**: Keep package.json files updated
5. **Regular Updates**: Run `npm run consolidate` regularly to get latest changes

## Technical Details

### NPM Workspaces

This monorepo uses NPM workspaces to manage multiple packages. The root `package.json` defines workspace patterns:

```json
"workspaces": [
  "packages/rotem/*",
  "packages/gemini/*",
  "packages/ai-platforms/*",
  "packages/tools/*",
  "packages/infrastructure/*"
]
```

### Turbo

We use Turbo for fast, parallel builds and caching:
- Builds only what changed
- Caches build outputs
- Runs tasks in parallel
- Manages task dependencies

### Git Strategy

Each sub-project maintains its own git repository:
- Original commit history is preserved
- Can still push/pull from original repos
- Monorepo provides an umbrella organization

## Migration Guide

If you're used to working with individual repositories:

**Before (individual repos)**:
```bash
git clone https://github.com/user/rotem_brain.git
cd rotem_brain
npm install
npm run dev
```

**After (monorepo)**:
```bash
git clone <monorepo-url>
cd unified-projects-monorepo
npm run bootstrap
cd packages/rotem/rotem_brain
npm run dev
```

## Future Enhancements

Potential improvements:
- [ ] Shared component library
- [ ] Unified testing infrastructure
- [x] Cross-project documentation
- [ ] Automated dependency updates
- [ ] Shared CI/CD pipelines
- [ ] Inter-project linking for development

---

**Questions?** Open an issue or consult the main README.md
