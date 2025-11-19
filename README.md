# Unified Projects Monorepo

This is a consolidated monorepo containing all AI and infrastructure projects.

## 📁 Structure

```
unified-projects-monorepo/
├── packages/
│   ├── rotem/              # RoTEM AI System Projects (7 projects)
│   │   ├── rotem-group-chat/
│   │   ├── rotem-ai-demo/
│   │   ├── RoTEM_Project/
│   │   ├── rotem_system/
│   │   ├── RoTEM_Dashboard/
│   │   ├── rotem_brain/
│   │   └── RoTEM/
│   ├── gemini/             # Gemini/Biju Projects (3 projects)
│   │   ├── GeminiBiju_Unified/
│   │   ├── gemini-cli/
│   │   └── gemini-biju/
│   ├── ai-platforms/       # AI Platform Projects (6 projects)
│   │   ├── ai-saas-platform1/
│   │   ├── btl-gpt-production-suite/
│   │   ├── AI-Empire/
│   │   ├── AIPROJ/
│   │   ├── UltimateAgentConsole/
│   │   └── premium-business-platform/
│   ├── tools/              # Development Tools (3 projects)
│   │   ├── claude-code/
│   │   ├── anthropic-sdk-python/
│   │   └── github-mcp-server/
│   └── infrastructure/     # Infrastructure Projects (4 projects)
│       ├── tailscale/
│       ├── firebaseui-web/
│       ├── TheVortex_v4/
│       └── echosync-v6/
├── tools/                  # Monorepo management scripts
│   └── consolidate-projects.js
└── docs/                   # Shared documentation
```

## 🚀 Quick Start

### Initial Setup

```bash
# Clone this repository
git clone <your-repo-url>
cd unified-projects-monorepo

# Run consolidation (clones all sub-projects)
npm run bootstrap
```

### Working with Projects

```bash
# Install all dependencies
npm install

# Build all projects
npm run build:all

# Test all projects
npm run test:all

# Work on a specific project
cd packages/rotem/rotem_brain
npm install
npm run dev
```

### Adding New Projects

Edit `tools/consolidate-projects.js` and add your project to the appropriate category, then run:

```bash
npm run consolidate
```

## 📦 Project Categories

### 🧠 RoTEM Projects
Advanced AI system with multiple components:
- **rotem_brain**: Core AI engine
- **RoTEM_Dashboard**: Management interface
- **rotem_system**: System coordination
- **rotem-group-chat**: Multi-agent chat
- **rotem-ai-demo**: Demonstration applications
- **RoTEM_Project**: Main project
- **RoTEM**: Base implementation

### 💎 Gemini Projects
Gemini/Biju AI implementation:
- **GeminiBiju_Unified**: Unified platform
- **gemini-cli**: Command-line interface
- **gemini-biju**: Core functionality

### 🤖 AI Platforms
Enterprise AI platforms and tools:
- **ai-saas-platform1**: SaaS platform
- **btl-gpt-production-suite**: Production suite
- **AI-Empire**: Empire management
- **AIPROJ**: AI project tools
- **UltimateAgentConsole**: Agent management
- **premium-business-platform**: Business platform

### 🛠️ Development Tools
SDKs and development utilities:
- **claude-code**: Claude coding tools
- **anthropic-sdk-python**: Python SDK
- **github-mcp-server**: GitHub MCP server

### 🏗️ Infrastructure
Core infrastructure and services:
- **tailscale**: Network infrastructure
- **firebaseui-web**: Firebase UI
- **TheVortex_v4**: Vortex platform
- **echosync-v6**: Sync service

## 🔧 Management Scripts

```bash
# Re-consolidate all projects (pull latest changes)
npm run consolidate

# Clean all node_modules
npm run clean

# Bootstrap from scratch
npm run bootstrap
```

## 📝 Development Workflow

1. **Make changes** in the specific package directory
2. **Test locally** within that package
3. **Build** if needed
4. **Commit** changes to this monorepo
5. **Push** to remote

## 🤝 Contributing

Each project maintains its own:
- Dependencies
- Build scripts
- Testing setup
- Documentation

Refer to individual project READMEs for specific contribution guidelines.

## 📄 License

See individual project licenses in their respective directories.

## 🎯 Project Status

Total Projects: 23
- RoTEM: 7 projects
- Gemini: 3 projects
- AI Platforms: 6 projects
- Tools: 3 projects
- Infrastructure: 4 projects

---

**Last Updated**: 2025-11-19
**Monorepo Version**: 1.0.0
