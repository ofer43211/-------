# 🚀 Quick Start Guide

Welcome to the Unified Projects Monorepo! Here's how to get started in 5 minutes.

## Step 1: Clone All Projects (First Time Only)

```bash
# Install Node.js dependencies and clone all projects
npm run bootstrap
```

This will:
- Install the monorepo tools (Lerna, Turbo)
- Clone all 23 projects from GitHub
- Organize them into `packages/` directory

**Note**: This may take 5-10 minutes depending on your internet connection.

## Step 2: Explore the Structure

```bash
# See what got cloned
ls -la packages/

# You should see:
# - packages/rotem/          (7 RoTEM projects)
# - packages/gemini/         (3 Gemini projects)
# - packages/ai-platforms/   (6 AI platform projects)
# - packages/tools/          (3 development tools)
# - packages/infrastructure/ (4 infrastructure projects)
```

## Step 3: Work on a Project

### Option A: Use the Interactive Runner

```bash
# Run the interactive project selector
./tools/run-project.sh
```

This will:
1. Show you all categories
2. Let you pick a project
3. Show available commands
4. Run the command you select

### Option B: Manual Navigation

```bash
# Example: Work on RoTEM Brain
cd packages/rotem/rotem_brain

# Install dependencies
npm install

# Run development server
npm run dev
```

## Common Commands

### Update All Projects

Pull latest changes from all repositories:

```bash
npm run consolidate
```

### Build Everything

Build all projects in the monorepo:

```bash
npm run build:all
```

### Test Everything

Run tests across all projects:

```bash
npm run test:all
```

### Clean Everything

Remove all node_modules to start fresh:

```bash
npm run clean
npm run bootstrap
```

## Working with Specific Project Categories

### 🧠 RoTEM Projects (AI System)

```bash
cd packages/rotem/rotem_brain
npm install
npm run dev
```

### 💎 Gemini Projects

```bash
cd packages/gemini/gemini-cli
npm install
npm run dev
```

### 🤖 AI Platforms

```bash
cd packages/ai-platforms/ai-saas-platform1
npm install
npm run dev
```

### 🛠️ Development Tools

```bash
cd packages/tools/claude-code
npm install
npm run dev
```

### 🏗️ Infrastructure

```bash
cd packages/infrastructure/tailscale
npm install
npm run dev
```

## Troubleshooting

### "npm run bootstrap" fails

Make sure you have Node.js 18+ installed:

```bash
node --version  # Should be v18.0.0 or higher
npm --version   # Should be v9.0.0 or higher
```

### A specific project won't clone

Check the URL in `tools/consolidate-projects.js` and your GitHub access.

### Dependencies won't install

```bash
# Clean and try again
rm -rf node_modules
npm install
```

### Build fails

Try building just one project to isolate the issue:

```bash
cd packages/rotem/rotem_brain
npm install
npm run build
```

## Next Steps

- 📖 Read [README.md](./README.md) for full documentation
- 📚 Read [docs/CONSOLIDATION.md](./docs/CONSOLIDATION.md) for detailed guide
- 🔍 Explore individual project READMEs in `packages/`

## Project Overview

| Category | Projects | Description |
|----------|----------|-------------|
| 🧠 RoTEM | 7 | Advanced AI system components |
| 💎 Gemini | 3 | Gemini/Biju AI platform |
| 🤖 AI Platforms | 6 | Enterprise AI platforms |
| 🛠️ Tools | 3 | Development tools & SDKs |
| 🏗️ Infrastructure | 4 | Core infrastructure |

**Total: 23 Projects**

## Need Help?

- Check [docs/CONSOLIDATION.md](./docs/CONSOLIDATION.md)
- Look at project-specific README files
- Open an issue if something's broken

---

**Happy Coding!** 🎉
