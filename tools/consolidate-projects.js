#!/usr/bin/env node

/**
 * Project Consolidation Script
 * This script clones and organizes all projects into the monorepo structure
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Project definitions with their GitHub URLs and target locations
const PROJECTS = {
  rotem: [
    { name: 'rotem-group-chat', url: 'https://github.com/ofer43211/rotem-group-chat.git' },
    { name: 'rotem-ai-demo', url: 'https://github.com/ofer43211/rotem-ai-demo.git' },
    { name: 'RoTEM_Project', url: 'https://github.com/ofer43211/RoTEM_Project.git' },
    { name: 'rotem_system', url: 'https://github.com/ofer43211/rotem_system.git' },
    { name: 'RoTEM_Dashboard', url: 'https://github.com/ofer43211/RoTEM_Dashboard.git' },
    { name: 'rotem_brain', url: 'https://github.com/ofer43211/rotem_brain.git' },
    { name: 'RoTEM', url: 'https://github.com/ofer43211/RoTEM.git' }
  ],
  gemini: [
    { name: 'GeminiBiju_Unified', url: 'https://github.com/ReachingOut/GeminiBiju_Unified.git' },
    { name: 'gemini-cli', url: 'https://github.com/ofer43211/gemini-cli.git' },
    { name: 'gemini-biju', url: 'https://github.com/ofer43211/gemini-biju.git' }
  ],
  'ai-platforms': [
    { name: 'ai-saas-platform1', url: 'https://github.com/ofer43211/ai-saas-platform1.git' },
    { name: 'btl-gpt-production-suite', url: 'https://github.com/ofer43211/btl-gpt-production-suite.git' },
    { name: 'AI-Empire', url: 'https://github.com/ofer43211/AI-Empire.git' },
    { name: 'AIPROJ', url: 'https://github.com/ofer43211/AIPROJ.git' },
    { name: 'UltimateAgentConsole', url: 'https://github.com/ofer43211/UltimateAgentConsole.git' },
    { name: 'premium-business-platform', url: 'https://github.com/ofer43211/-premium-business-platform.git' }
  ],
  tools: [
    { name: 'claude-code', url: 'https://github.com/ofer43211/claude-code.git' },
    { name: 'anthropic-sdk-python', url: 'https://github.com/ofer43211/anthropic-sdk-python.git' },
    { name: 'github-mcp-server', url: 'https://github.com/ofer43211/github-mcp-server.git' }
  ],
  infrastructure: [
    { name: 'tailscale', url: 'https://github.com/ofer43211/tailscale.git' },
    { name: 'firebaseui-web', url: 'https://github.com/ofer43211/firebaseui-web.git' },
    { name: 'TheVortex_v4', url: 'https://github.com/ofer43211/TheVortex_v4.git' },
    { name: 'echosync-v6', url: 'https://github.com/ofer43211/echosync-v6.git' }
  ]
};

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

function cloneOrUpdateProject(category, project) {
  const targetDir = path.join(__dirname, '..', 'packages', category, project.name);

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Processing: ${project.name}`);
  console.log(`Category: ${category}`);
  console.log(`Target: ${targetDir}`);
  console.log(`${'='.repeat(60)}`);

  if (fs.existsSync(targetDir)) {
    console.log(`⟳ Updating existing project...`);
    try {
      exec('git pull', { cwd: targetDir });
      console.log(`✓ Updated ${project.name}`);
    } catch (error) {
      console.error(`⚠ Failed to update ${project.name}`);
    }
  } else {
    console.log(`⤓ Cloning new project...`);
    ensureDirectory(path.join(__dirname, '..', 'packages', category));
    try {
      exec(`git clone ${project.url} "${targetDir}"`);
      console.log(`✓ Cloned ${project.name}`);
    } catch (error) {
      console.error(`⚠ Failed to clone ${project.name}`);
    }
  }
}

function createCategoryReadme(category, projects) {
  const dir = path.join(__dirname, '..', 'packages', category);
  ensureDirectory(dir);

  const readme = `# ${category.charAt(0).toUpperCase() + category.slice(1)} Projects

This directory contains the following projects:

${projects.map(p => `- **${p.name}**: ${p.url}`).join('\n')}

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

  // Create base directory structure
  console.log('📁 Creating directory structure...\n');
  Object.keys(PROJECTS).forEach(category => {
    ensureDirectory(path.join(__dirname, '..', 'packages', category));
  });

  // Clone/update all projects
  console.log('\n📦 Cloning/updating projects...\n');
  for (const [category, projects] of Object.entries(PROJECTS)) {
    console.log(`\n▶ Processing ${category} projects...`);
    for (const project of projects) {
      cloneOrUpdateProject(category, project);
    }
    createCategoryReadme(category, projects);
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ Consolidation complete!');
  console.log('='.repeat(60));
  console.log('\nNext steps:');
  console.log('1. Review the consolidated structure in packages/');
  console.log('2. Run "npm install" to install dependencies');
  console.log('3. Run "npm run build:all" to build all projects');
  console.log('\n');
}

// Run the script
main().catch(error => {
  console.error('❌ Consolidation failed:', error);
  process.exit(1);
});
