#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const categories = {
  rotem: [
    'rotem-group-chat',
    'rotem-ai-demo',
    'RoTEM_Project',
    'rotem_system',
    'RoTEM_Dashboard',
    'rotem_brain',
    'RoTEM',
  ],
  gemini: ['GeminiBiju_Unified', 'gemini-cli', 'gemini-biju'],
  'ai-platforms': [
    'ai-saas-platform1',
    'btl-gpt-production-suite',
    'AI-Empire',
    'AIPROJ',
    'UltimateAgentConsole',
    'premium-business-platform',
  ],
  tools: ['claude-code', 'anthropic-sdk-python', 'github-mcp-server'],
  infrastructure: ['tailscale', 'firebaseui-web', 'TheVortex_v4', 'echosync-v6'],
};

const results = [];
let totalFound = 0;
let totalExpected = 0;

console.log('📦 Project availability check');
console.log('==============================');
console.log('');

for (const [category, projects] of Object.entries(categories)) {
  console.log(`Category: ${category}`);
  const categoryPath = path.join('packages', category);
  projects.forEach((project) => {
    const projectPath = path.join(categoryPath, project);
    const exists = fs.existsSync(projectPath);
    const status = exists ? 'present' : 'missing';
    results.push({ category, project, status, projectPath });
    totalExpected += 1;
    if (exists) totalFound += 1;
    console.log(`  - ${project}: ${exists ? '✅ present' : '❌ missing'} (${projectPath})`);
  });
  console.log('');
}

const totalMissing = totalExpected - totalFound;
console.log('Summary');
console.log('-------');
console.log(`Found: ${totalFound}/${totalExpected}`);
console.log(`Missing: ${totalMissing}`);

if (totalMissing > 0) {
  const missingByCategory = results.filter((r) => r.status === 'missing').reduce((acc, r) => {
    acc[r.category] = acc[r.category] || [];
    acc[r.category].push(r.project);
    return acc;
  }, {});

  console.log('\nMissing projects by category:');
  Object.entries(missingByCategory).forEach(([category, projects]) => {
    console.log(`- ${category}: ${projects.join(', ')}`);
  });
}
