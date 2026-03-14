#!/usr/bin/env node

/**
 * Inter-Project Linking Tool
 *
 * Creates symlinks between sub-projects so they can import from each other
 * during local development without publishing to a registry.
 *
 * Usage:
 *   node tools/link-projects.js                  # Link all shared packages into all sub-projects
 *   node tools/link-projects.js --status         # Show current link status
 *   node tools/link-projects.js --clean          # Remove all created links
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PACKAGES_DIR = path.join(ROOT, 'packages');

const SHARED_PACKAGES = [
  { name: '@unified/ui', dir: path.join(PACKAGES_DIR, 'shared', 'ui') },
  { name: '@unified/utils', dir: path.join(PACKAGES_DIR, 'shared', 'utils') },
];

const CATEGORIES = ['rotem', 'gemini', 'ai-platforms', 'tools', 'infrastructure'];

function findSubProjects() {
  const projects = [];
  for (const category of CATEGORIES) {
    const categoryDir = path.join(PACKAGES_DIR, category);
    if (!fs.existsSync(categoryDir)) continue;

    const entries = fs.readdirSync(categoryDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const projectDir = path.join(categoryDir, entry.name);
      const pkgPath = path.join(projectDir, 'package.json');
      if (fs.existsSync(pkgPath)) {
        projects.push({ name: entry.name, dir: projectDir, category });
      }
    }
  }
  return projects;
}

function ensureScope(nodeModulesDir, scope) {
  const scopeDir = path.join(nodeModulesDir, scope);
  if (!fs.existsSync(scopeDir)) {
    fs.mkdirSync(scopeDir, { recursive: true });
  }
}

function linkSharedIntoProject(project, sharedPkg) {
  const nodeModulesDir = path.join(project.dir, 'node_modules');
  if (!fs.existsSync(nodeModulesDir)) {
    fs.mkdirSync(nodeModulesDir, { recursive: true });
  }

  const scope = sharedPkg.name.split('/')[0];
  ensureScope(nodeModulesDir, scope);

  const linkPath = path.join(nodeModulesDir, sharedPkg.name);

  if (fs.existsSync(linkPath)) {
    const stat = fs.lstatSync(linkPath);
    if (stat.isSymbolicLink()) {
      return 'already-linked';
    }
    return 'skipped-exists';
  }

  fs.symlinkSync(sharedPkg.dir, linkPath, 'dir');
  return 'linked';
}

function cleanLinks(project, sharedPkg) {
  const linkPath = path.join(project.dir, 'node_modules', sharedPkg.name);
  if (fs.existsSync(linkPath) && fs.lstatSync(linkPath).isSymbolicLink()) {
    fs.unlinkSync(linkPath);
    return 'removed';
  }
  return 'not-found';
}

function checkStatus(project, sharedPkg) {
  const linkPath = path.join(project.dir, 'node_modules', sharedPkg.name);
  if (!fs.existsSync(linkPath)) return 'missing';
  if (fs.lstatSync(linkPath).isSymbolicLink()) return 'linked';
  return 'installed';
}

function main() {
  const args = process.argv.slice(2);
  const isClean = args.includes('--clean');
  const isStatus = args.includes('--status');

  const sharedAvailable = SHARED_PACKAGES.filter(pkg => fs.existsSync(pkg.dir));
  if (sharedAvailable.length === 0) {
    console.log('No shared packages found. Create packages under packages/shared/ first.');
    return;
  }

  const subProjects = findSubProjects();
  if (subProjects.length === 0) {
    console.log('No sub-projects found. Run "npm run consolidate" first.');
    return;
  }

  console.log(`\nShared packages: ${sharedAvailable.map(p => p.name).join(', ')}`);
  console.log(`Sub-projects found: ${subProjects.length}\n`);

  if (isStatus) {
    console.log('Link status:');
    console.log('─'.repeat(60));
    for (const project of subProjects) {
      for (const pkg of sharedAvailable) {
        const status = checkStatus(project, pkg);
        const icon = status === 'linked' ? '🔗' : status === 'installed' ? '📦' : '  ';
        console.log(`  ${icon} ${project.category}/${project.name} → ${pkg.name}: ${status}`);
      }
    }
    return;
  }

  if (isClean) {
    console.log('Removing links...');
    for (const project of subProjects) {
      for (const pkg of sharedAvailable) {
        const result = cleanLinks(project, pkg);
        if (result === 'removed') {
          console.log(`  ✓ Removed ${pkg.name} from ${project.name}`);
        }
      }
    }
    console.log('\nDone.');
    return;
  }

  console.log('Linking shared packages into sub-projects...');
  let linked = 0;
  let skipped = 0;
  for (const project of subProjects) {
    for (const pkg of sharedAvailable) {
      const result = linkSharedIntoProject(project, pkg);
      if (result === 'linked') {
        console.log(`  🔗 ${pkg.name} → ${project.category}/${project.name}`);
        linked++;
      } else if (result === 'already-linked') {
        skipped++;
      } else if (result === 'skipped-exists') {
        console.log(`  ⏭  ${pkg.name} in ${project.name} (non-symlink exists, skipped)`);
        skipped++;
      }
    }
  }
  console.log(`\n✅ Done: ${linked} links created, ${skipped} skipped.`);
  console.log('\nSub-projects can now import from shared packages:');
  console.log('  import { Logger } from \'@unified/utils\';');
  console.log('  import { Button } from \'@unified/ui\';');
}

main();
