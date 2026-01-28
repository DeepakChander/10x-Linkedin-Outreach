#!/usr/bin/env node
/**
 * 10x Outreach Skill — Pre-install environment checker
 * Validates Node, Python, npm, git, and creates required directories.
 * Run: node scripts/setup-check.js
 */

import { execSync } from 'child_process';
import { existsSync, mkdirSync, copyFileSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = join(__dirname, '..');

const REQUIRED_NODE = '18.0.0';
const REQUIRED_PYTHON = '3.9';

let errors = 0;
let warnings = 0;

function ok(msg) { console.log(`  ✓ ${msg}`); }
function warn(msg) { warnings++; console.log(`  ⚠ ${msg}`); }
function fail(msg) { errors++; console.log(`  ✗ ${msg}`); }

function semverGte(a, b) {
  const pa = a.split('.').map(Number);
  const pb = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if ((pa[i] || 0) > (pb[i] || 0)) return true;
    if ((pa[i] || 0) < (pb[i] || 0)) return false;
  }
  return true;
}

function getVersion(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } catch { return null; }
}

function getOsInstallHint(tool) {
  const p = process.platform;
  const hints = {
    node: {
      win32: 'winget install OpenJS.NodeJS.LTS',
      darwin: 'brew install node@18',
      linux: 'curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs',
    },
    python: {
      win32: 'winget install Python.Python.3.12',
      darwin: 'brew install python@3.12',
      linux: 'sudo apt-get install -y python3 python3-pip',
    },
    git: {
      win32: 'winget install Git.Git',
      darwin: 'xcode-select --install',
      linux: 'sudo apt-get install -y git',
    },
  };
  return (hints[tool] && hints[tool][p]) || `Install ${tool} from its official website`;
}

console.log('\n🔍 10x Outreach Skill — Environment Check\n');

// --- Node.js ---
console.log('Node.js:');
const nodeV = getVersion('node -v');
if (nodeV) {
  const ver = nodeV.replace('v', '');
  if (semverGte(ver, REQUIRED_NODE)) {
    ok(`Node ${ver} (>= ${REQUIRED_NODE})`);
  } else {
    fail(`Node ${ver} is too old. Need >= ${REQUIRED_NODE}`);
    console.log(`    → ${getOsInstallHint('node')}`);
  }
} else {
  fail(`Node.js not found`);
  console.log(`    → ${getOsInstallHint('node')}`);
}

// --- npm ---
const npmV = getVersion('npm -v');
if (npmV) { ok(`npm ${npmV}`); }
else { fail('npm not found'); }

// --- Python ---
console.log('Python:');
let pyCmd = null;
for (const cmd of ['python3 --version', 'python --version']) {
  const v = getVersion(cmd);
  if (v) {
    const ver = v.replace(/Python\s*/i, '');
    const major = parseInt(ver.split('.')[0]);
    const minor = parseInt(ver.split('.')[1]);
    if (major >= 3 && minor >= 9) {
      ok(`Python ${ver} (>= ${REQUIRED_PYTHON})`);
      pyCmd = cmd.split(' ')[0];
      break;
    } else if (major >= 3) {
      warn(`Python ${ver} found. Recommended >= ${REQUIRED_PYTHON}`);
      pyCmd = cmd.split(' ')[0];
      break;
    }
  }
}
if (!pyCmd) {
  warn(`Python 3.9+ not found (needed for scripts)`);
  console.log(`    → ${getOsInstallHint('python')}`);
}

// --- Git ---
console.log('Git:');
const gitV = getVersion('git --version');
if (gitV) { ok(gitV); }
else { fail('git not found'); console.log(`    → ${getOsInstallHint('git')}`); }

// --- Directories ---
console.log('Directories:');
const dirs = [
  'campaigns/active', 'campaigns/completed', 'campaigns/logs',
  'output/workflows', 'output/logs', 'output/discovery', 'output/drafts', 'output/reports', 'output/sent',
  'credentials/profiles',
  'knowledge_base', 'tickets/active', 'tickets/closed',
  'audit_logs', 'tenants', 'webhooks', 'metrics',
];
let created = 0;
for (const d of dirs) {
  const full = join(ROOT, d);
  if (!existsSync(full)) {
    mkdirSync(full, { recursive: true });
    created++;
  }
}
if (created > 0) ok(`Created ${created} missing directories`);
else ok('All directories exist');

// --- .env ---
console.log('Environment:');
const envFile = join(ROOT, '.env');
const envExample = join(ROOT, '.env.example');
if (!existsSync(envFile) && existsSync(envExample)) {
  copyFileSync(envExample, envFile);
  ok('Created .env from .env.example');
} else if (existsSync(envFile)) {
  ok('.env exists');
} else {
  warn('No .env or .env.example found');
}

// --- Canvas ---
console.log('Canvas:');
const canvasPkg = join(ROOT, 'tldraw-canvas', 'package.json');
const canvasModules = join(ROOT, 'tldraw-canvas', 'node_modules');
if (existsSync(canvasPkg)) {
  ok('tldraw-canvas/package.json found');
  if (!existsSync(canvasModules)) {
    warn('tldraw-canvas/node_modules missing — run: cd tldraw-canvas && npm install');
  } else {
    ok('tldraw-canvas dependencies installed');
  }
} else {
  fail('tldraw-canvas/package.json not found');
}

// --- Python packages ---
if (pyCmd) {
  console.log('Python packages:');
  const required = ['dotenv', 'jinja2', 'yaml', 'requests'];
  for (const pkg of required) {
    const check = getVersion(`${pyCmd} -c "import ${pkg}; print('ok')" 2>&1`);
    if (check && check.includes('ok')) {
      ok(`${pkg}`);
    } else {
      warn(`${pkg} not installed — pip install ${pkg === 'dotenv' ? 'python-dotenv' : pkg === 'yaml' ? 'pyyaml' : pkg}`);
    }
  }
}

// --- Summary ---
console.log('\n' + '─'.repeat(50));
if (errors > 0) {
  console.log(`\n❌ ${errors} critical issue(s) found. Fix them before continuing.\n`);
  process.exit(1);
} else if (warnings > 0) {
  console.log(`\n⚠ ${warnings} warning(s). Setup can proceed but some features may not work.\n`);
} else {
  console.log('\n✅ Environment ready. Run: cd tldraw-canvas && npm install\n');
}
