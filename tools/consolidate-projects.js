#!/usr/bin/env node

/**
 * Project Consolidation Script
 * This script clones and organizes all projects into the monorepo structure.
 * It detects the local git proxy from the monorepo's remote origin URL and
 * uses it for cloning, falling back to direct GitHub URLs when no proxy is
 * available.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Project definitions — org + name; the clone URL is built at runtime.
const PROJECTS = {
  rotem: [
    { name: 'rotem-group-chat', org: 'ofer43211' },
    { name: 'rotem-ai-demo', org: 'ofer43211' },
    { name: 'RoTEM_Project', org: 'ofer43211' },
    { name: 'rotem_system', org: 'ofer43211' },
    { name: 'RoTEM_Dashboard', org: 'ofer43211' },
    { name: 'rotem_brain', org: 'ofer43211' },
    { name: 'RoTEM', org: 'ofer43211' }
  ],
  gemini: [
    { name: 'GeminiBiju_Unified', org: 'ReachingOut' },
    { name: 'gemini-cli', org: 'ofer43211' },
    { name: 'gemini-biju', org: 'ofer43211' }
  ],
  'ai-platforms': [
    { name: 'ai-saas-platform1', org: 'ofer43211' },
    { name: 'btl-gpt-production-suite', org: 'ofer43211' },
    { name: 'AI-Empire', org: 'ofer43211' },
    { name: 'AIPROJ', org: 'ofer43211' },
    { name: 'UltimateAgentConsole', org: 'ofer43211' },
    { name: 'premium-business-platform', org: 'ofer43211' }
  ],
  tools: [
    { name: 'claude-code', org: 'ofer43211' },
    { name: 'anthropic-sdk-python', org: 'ofer43211' },
    { name: 'github-mcp-server', org: 'ofer43211' }
  ],
  infrastructure: [
    { name: 'tailscale', org: 'ofer43211' },
    { name: 'firebaseui-web', org: 'ofer43211' },
    { name: 'TheVortex_v4', org: 'ofer43211' },
    { name: 'echosync-v6', org: 'ofer43211' }
  ]
};

/**
 * Detect the local proxy base URL from the monorepo's own remote origin.
 * Returns e.g. "http://local_proxy@127.0.0.1:55685/git" or null.
 */
function detectProxyBase() {
  try {
    const originUrl = execSync('git config --get remote.origin.url', {
      encoding: 'utf-8',
      cwd: path.join(__dirname, '..'),
    }).trim();
    const match = originUrl.match(/^(http:\/\/local_proxy@127\.0\.0\.1:\d+\/git)\//);
    if (match) return match[1];
  } catch (_) {
    // not inside a git repo or no remote — fall through
  }
  return null;
}

/**
 * Build the clone URL for a project.
 * When a local proxy is available we use it; otherwise fall back to GitHub.
 */
function cloneUrl(project, proxyBase) {
  if (proxyBase) {
    return `${proxyBase}/${project.org}/${project.name}`;
  }
  return `https://github.com/${project.org}/${project.name}.git`;
}

function exec(command, options = {}) {
  try {
    return execSync(command, {
      stdio: 'inherit',
      ...options
    });
  } catch (error) {
    console.error(`Error executing: ${command}`);
    throw error;
  }
}

function ensureDirectory(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`✓ Created directory: ${dir}`);
  }
}

function cloneOrUpdateProject(category, project, proxyBase) {
  const targetDir = path.join(__dirname, '..', 'packages', category, project.name);
  const url = cloneUrl(project, proxyBase);

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Processing: ${project.name}`);
  console.log(`Category: ${category}`);
  console.log(`URL: ${url}`);
  console.log(`${'='.repeat(60)}`);

  if (fs.existsSync(path.join(targetDir, '.git'))) {
    console.log(`⟳ Updating existing project...`);
    try {
      exec('git pull', { cwd: targetDir });
      console.log(`✓ Updated ${project.name}`);
      return 'updated';
    } catch (error) {
      console.error(`⚠ Failed to update ${project.name}`);
      return 'failed';
    }
  } else {
    // Remove leftover directory (e.g. empty dir from a previous failed clone)
    if (fs.existsSync(targetDir)) {
      fs.rmSync(targetDir, { recursive: true });
    }
    console.log(`⤓ Cloning new project...`);
    ensureDirectory(path.join(__dirname, '..', 'packages', category));
    try {
      exec(`git clone "${url}" "${targetDir}"`);
      console.log(`✓ Cloned ${project.name}`);
      return 'cloned';
    } catch (error) {
      console.error(`⚠ Failed to clone ${project.name} (likely private / not authorized)`);
      return 'failed';
    }
  }
}

function createCategoryReadme(category, projects) {
  const dir = path.join(__dirname, '..', 'packages', category);
  ensureDirectory(dir);

  const readme = `# ${category.charAt(0).toUpperCase() + category.slice(1)} Projects

This directory contains the following projects:

${projects.map(p => `- **${p.name}**: https://github.com/${p.org}/${p.name}`).join('\n')}

## Structure

Each project maintains its own:
- Dependencies (package.json)
- Build configuration
- Tests
- Documentation

## Development

To work on a specific project:
\`\`\`bash
cd packages/${category}/<project-name>
npm install
npm run dev
\`\`\`
`;

  fs.writeFileSync(path.join(dir, 'README.md'), readme);
  console.log(`✓ Created README for ${category}`);
}

async function main() {
  console.log('\n🚀 Starting Project Consolidation\n');

  const proxyBase = detectProxyBase();
  if (proxyBase) {
    console.log(`🔗 Detected local proxy: ${proxyBase}\n`);
  } else {
    console.log('🌐 No local proxy detected — using direct GitHub URLs\n');
  }

  // Create base directory structure
  console.log('📁 Creating directory structure...\n');
  Object.keys(PROJECTS).forEach(category => {
    ensureDirectory(path.join(__dirname, '..', 'packages', category));
  });

  // Clone/update all projects
  const stats = { cloned: 0, updated: 0, failed: 0 };
  const failures = [];

  console.log('\n📦 Cloning/updating projects...\n');
  for (const [category, projects] of Object.entries(PROJECTS)) {
    console.log(`\n▶ Processing ${category} projects...`);
    for (const project of projects) {
      const result = cloneOrUpdateProject(category, project, proxyBase);
      stats[result] = (stats[result] || 0) + 1;
      if (result === 'failed') {
        failures.push(`${category}/${project.name}`);
      }
    }
    createCategoryReadme(category, projects);
  }

  const total = stats.cloned + stats.updated + stats.failed;
  console.log('\n' + '='.repeat(60));
  console.log('📊 Consolidation Summary');
  console.log('='.repeat(60));
  console.log(`  Total:   ${total}`);
  console.log(`  Cloned:  ${stats.cloned}`);
  console.log(`  Updated: ${stats.updated}`);
  console.log(`  Failed:  ${stats.failed}`);

  if (failures.length > 0) {
    console.log(`\n⚠ Failed projects (private / not authorized):`);
    failures.forEach(f => console.log(`  - ${f}`));
    console.log('\nTo clone private repos, ensure GitHub authentication is configured');
    console.log('and re-run: npm run consolidate');
  }

  console.log('\n✅ Done.\n');
}

// Run the script
main().catch(error => {
  console.error('❌ Consolidation failed:', error);
  process.exit(1);
});
