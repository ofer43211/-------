# Private Repositories Guide

## Successfully Cloned (Public Repositories) ✅

The following 10 projects were successfully cloned:

### RoTEM Projects (1/7)
- ✅ rotem-ai-demo

### Gemini Projects (1/3)
- ✅ gemini-cli

### AI Platforms (2/6)
- ✅ ai-saas-platform1
- ✅ premium-business-platform

### Tools (3/3)
- ✅ claude-code
- ✅ anthropic-sdk-python
- ✅ github-mcp-server

### Infrastructure (3/4)
- ✅ tailscale
- ✅ firebaseui-web
- ✅ echosync-v6

## Private Repositories (Require Authentication) 🔒

The following 13 projects are private and require GitHub authentication:

### RoTEM Projects (6/7)
- 🔒 rotem-group-chat
- 🔒 RoTEM_Project
- 🔒 rotem_system
- 🔒 RoTEM_Dashboard
- 🔒 rotem_brain
- 🔒 RoTEM

### Gemini Projects (2/3)
- 🔒 GeminiBiju_Unified (ReachingOut org)
- 🔒 gemini-biju

### AI Platforms (4/6)
- 🔒 btl-gpt-production-suite
- 🔒 AI-Empire
- 🔒 AIPROJ
- 🔒 UltimateAgentConsole

### Infrastructure (1/4)
- 🔒 TheVortex_v4

## How to Clone Private Repositories

There are several ways to add the private repositories:

### Option 1: Using GitHub CLI (Recommended)

```bash
# Login to GitHub
gh auth login

# Clone private repos manually
cd packages/rotem
gh repo clone ofer43211/rotem-group-chat
gh repo clone ofer43211/RoTEM_Project
gh repo clone ofer43211/rotem_system
gh repo clone ofer43211/RoTEM_Dashboard
gh repo clone ofer43211/rotem_brain
gh repo clone ofer43211/RoTEM

cd ../gemini
gh repo clone ReachingOut/GeminiBiju_Unified
gh repo clone ofer43211/gemini-biju

cd ../ai-platforms
gh repo clone ofer43211/btl-gpt-production-suite
gh repo clone ofer43211/AI-Empire
gh repo clone ofer43211/AIPROJ
gh repo clone ofer43211/UltimateAgentConsole

cd ../infrastructure
gh repo clone ofer43211/TheVortex_v4
```

### Option 2: Using SSH URLs

Update `tools/consolidate-projects.js` to use SSH URLs instead of HTTPS:

```javascript
// Change from:
{ name: 'rotem_brain', url: 'https://github.com/ofer43211/rotem_brain.git' }

// To:
{ name: 'rotem_brain', url: 'git@github.com:ofer43211/rotem_brain.git' }
```

Then configure SSH keys:
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub: https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub
```

### Option 3: Using Personal Access Token

```bash
# Create token at: https://github.com/settings/tokens
# Clone with token
git clone https://YOUR_TOKEN@github.com/ofer43211/rotem_brain.git
```

### Option 4: Manual Clone

For each private repo:

```bash
cd packages/rotem
git clone https://github.com/ofer43211/rotem_brain.git
# Enter your GitHub credentials when prompted
```

## Checking Access

Verify you have access to the private repositories:

```bash
# Using GitHub CLI
gh repo view ofer43211/rotem_brain

# Using git
git ls-remote https://github.com/ofer43211/rotem_brain.git
```

## Current Status

**Total Projects**: 23
- ✅ **Public & Cloned**: 10 projects
- 🔒 **Private (Need Auth)**: 13 projects

Once you've added authentication, run the consolidation script again:

```bash
npm run consolidate
```

This will update existing public repos and clone the private ones.

## Tips

1. **SSH is recommended** for private repos (no password prompts)
2. **Use GitHub CLI** for easiest authentication
3. **Personal Access Tokens** work but expire
4. **HTTPS + credentials** requires entering password each time

---

Need help setting up authentication? Check:
- [GitHub SSH Keys Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub CLI Installation](https://cli.github.com/)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
