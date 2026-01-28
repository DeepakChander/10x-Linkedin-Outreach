#!/usr/bin/env node

/**
 * 10x-Outreach-Skill Interactive Setup Wizard
 *
 * This script guides users through setting up their environment
 * by collecting API keys and configuration interactively.
 */

import * as readline from 'readline';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
};

// Helper functions for colored output
const log = {
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  info: (msg) => console.log(`${colors.cyan}ℹ${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bright}${colors.magenta}${msg}${colors.reset}`),
  section: (msg) => console.log(`\n${colors.bright}${colors.cyan}${msg}${colors.reset}`),
  dim: (msg) => console.log(`${colors.dim}${msg}${colors.reset}`),
};

// Configuration structure
const config = {
  required: {
    EXA_API_KEY: {
      prompt: 'Exa AI API Key',
      description: 'Required for prospect enrichment and discovery',
      getUrl: 'https://exa.ai',
      features: [
        'Prospect enrichment',
        'Company data lookup',
        'Social profile discovery',
      ],
    },
    GOOGLE_CLIENT_ID: {
      prompt: 'Google Client ID',
      description: 'Required for Gmail integration',
      getUrl: 'https://console.cloud.google.com/',
      features: ['Email sending via Gmail'],
    },
    GOOGLE_CLIENT_SECRET: {
      prompt: 'Google Client Secret',
      description: 'Required for Gmail integration',
      getUrl: 'https://console.cloud.google.com/',
      features: ['Email sending via Gmail'],
    },
    SENDER_EMAIL: {
      prompt: 'Sender Email (Gmail address)',
      description: 'Your Gmail address for sending emails',
      features: ['Email campaigns', 'Outreach automation'],
      validate: (value) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value) || 'Please enter a valid email address';
      },
    },
  },
  optional: {
    GEMINI_API_KEY: {
      prompt: 'Gemini AI API Key',
      description: 'Optional - enables multimodal features',
      getUrl: 'https://aistudio.google.com/apikey',
      features: [
        'Image analysis',
        'Video processing',
        'PDF extraction',
      ],
    },
    CANVA_CLIENT_ID: {
      prompt: 'Canva Client ID',
      description: 'Optional - enables design automation',
      getUrl: 'https://www.canva.com/developers/',
      features: ['Automated design generation', 'Template creation'],
    },
    CANVA_CLIENT_SECRET: {
      prompt: 'Canva Client Secret',
      description: 'Optional - enables design automation',
      getUrl: 'https://www.canva.com/developers/',
      features: ['Automated design generation', 'Template creation'],
    },
    CANVA_ACCESS_TOKEN: {
      prompt: 'Canva Access Token',
      description: 'Optional - enables design automation',
      getUrl: 'https://www.canva.com/developers/',
      features: ['Automated design generation', 'Template creation'],
    },
    ANTHROPIC_API_KEY: {
      prompt: 'Anthropic API Key',
      description: 'Optional - for advanced AI features (will use Claude Code\'s key if not provided)',
      getUrl: 'https://console.anthropic.com/',
      features: ['Advanced AI features', 'Enhanced content generation'],
    },
  },
  defaults: {
    WORKSPACE_PATH: {
      prompt: 'Workspace Path',
      description: 'Directory for storing campaign data and outputs',
      default: '~/10x-skill-workspace',
    },
    CANVAS_PORT: {
      prompt: 'Canvas Port',
      description: 'Port for the visual canvas server',
      default: '3000',
    },
    DEBUG: {
      prompt: 'Enable Debug Mode',
      description: 'Enable detailed logging (true/false)',
      default: 'false',
      validate: (value) => {
        return ['true', 'false'].includes(value.toLowerCase()) || 'Please enter "true" or "false"';
      },
    },
  },
};

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Prompt user for input
function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

// Display banner
function displayBanner() {
  console.clear();
  console.log(colors.magenta);
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║        10x-Outreach-Skill Interactive Setup Wizard          ║');
  console.log('║                                                              ║');
  console.log('║   This wizard will help you configure your environment       ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log(colors.reset);
}

// Display feature warnings
function displayFeatureInfo(key, configItem) {
  log.dim(`  Get your key: ${configItem.getUrl || 'N/A'}`);
  if (configItem.features && configItem.features.length > 0) {
    log.dim(`  Features enabled: ${configItem.features.join(', ')}`);
  }
}

// Collect configuration values
async function collectConfig() {
  const values = {};

  // Required configuration
  log.header('═══ REQUIRED CONFIGURATION ═══');
  log.info('These are essential for core functionality\n');

  for (const [key, configItem] of Object.entries(config.required)) {
    log.section(`${configItem.prompt}:`);
    log.dim(`  ${configItem.description}`);
    displayFeatureInfo(key, configItem);

    let value = '';
    let isValid = false;

    while (!isValid) {
      value = await question(`\n${colors.bright}Enter ${configItem.prompt}:${colors.reset} `);
      value = value.trim();

      if (!value) {
        log.error('This field is required. Please provide a value.');
        continue;
      }

      if (configItem.validate) {
        const validationResult = configItem.validate(value);
        if (validationResult === true) {
          isValid = true;
        } else {
          log.error(validationResult);
        }
      } else {
        isValid = true;
      }
    }

    values[key] = value;
    log.success(`${configItem.prompt} configured`);
  }

  // Optional configuration
  log.header('\n═══ OPTIONAL CONFIGURATION ═══');
  log.info('These enhance functionality but are not required\n');

  const skipOptional = await question(
    `${colors.yellow}Would you like to configure optional features? (y/n):${colors.reset} `
  );

  if (skipOptional.toLowerCase() === 'y') {
    for (const [key, configItem] of Object.entries(config.optional)) {
      log.section(`\n${configItem.prompt}:`);
      log.dim(`  ${configItem.description}`);
      displayFeatureInfo(key, configItem);

      const configure = await question(
        `\n${colors.bright}Configure ${configItem.prompt}? (y/n):${colors.reset} `
      );

      if (configure.toLowerCase() === 'y') {
        let value = '';
        let isValid = false;

        while (!isValid) {
          value = await question(`Enter ${configItem.prompt}: `);
          value = value.trim();

          if (!value) {
            log.warning('Skipping this optional field.');
            isValid = true;
            continue;
          }

          if (configItem.validate) {
            const validationResult = configItem.validate(value);
            if (validationResult === true) {
              isValid = true;
            } else {
              log.error(validationResult);
            }
          } else {
            isValid = true;
          }
        }

        if (value) {
          values[key] = value;
          log.success(`${configItem.prompt} configured`);
        }
      } else {
        log.dim(`  Skipped ${configItem.prompt}`);
      }
    }
  } else {
    log.info('Skipping optional configuration');
  }

  // Default configuration
  log.header('\n═══ WORKSPACE & SETTINGS ═══');

  for (const [key, configItem] of Object.entries(config.defaults)) {
    const value = await question(
      `${configItem.prompt} [${colors.dim}${configItem.default}${colors.reset}]: `
    );

    if (value.trim()) {
      if (configItem.validate) {
        const validationResult = configItem.validate(value.trim());
        if (validationResult === true) {
          values[key] = value.trim();
        } else {
          log.error(validationResult);
          values[key] = configItem.default;
        }
      } else {
        values[key] = value.trim();
      }
    } else {
      values[key] = configItem.default;
    }
  }

  return values;
}

// Generate .env file content
function generateEnvContent(values) {
  const lines = [
    '# 10x-Outreach-Skill Environment Configuration',
    '# Generated by setup wizard on ' + new Date().toISOString(),
    '',
    '# ============================================',
    '# REQUIRED: Exa AI (for prospect enrichment)',
    '# ============================================',
    `EXA_API_KEY=${values.EXA_API_KEY || ''}`,
    '',
    '# ============================================',
    '# REQUIRED: Gmail Integration',
    '# ============================================',
    `GOOGLE_CLIENT_ID=${values.GOOGLE_CLIENT_ID || ''}`,
    `GOOGLE_CLIENT_SECRET=${values.GOOGLE_CLIENT_SECRET || ''}`,
    `SENDER_EMAIL=${values.SENDER_EMAIL || ''}`,
    '',
  ];

  // Add optional configurations if provided
  if (values.GEMINI_API_KEY) {
    lines.push(
      '# ============================================',
      '# OPTIONAL: Gemini AI (for multimodal features)',
      '# ============================================',
      `GEMINI_API_KEY=${values.GEMINI_API_KEY}`,
      ''
    );
  }

  if (values.CANVA_CLIENT_ID || values.CANVA_CLIENT_SECRET || values.CANVA_ACCESS_TOKEN) {
    lines.push(
      '# ============================================',
      '# OPTIONAL: Canva Integration',
      '# ============================================',
      `CANVA_CLIENT_ID=${values.CANVA_CLIENT_ID || ''}`,
      `CANVA_CLIENT_SECRET=${values.CANVA_CLIENT_SECRET || ''}`,
      `CANVA_ACCESS_TOKEN=${values.CANVA_ACCESS_TOKEN || ''}`,
      ''
    );
  }

  if (values.ANTHROPIC_API_KEY) {
    lines.push(
      '# ============================================',
      '# OPTIONAL: Claude API',
      '# ============================================',
      `ANTHROPIC_API_KEY=${values.ANTHROPIC_API_KEY}`,
      ''
    );
  }

  // Add default configurations
  lines.push(
    '# ============================================',
    '# Browser Extension Settings',
    '# ============================================',
    `CANVAS_PORT=${values.CANVAS_PORT || '3000'}`,
    'CANVAS_HOST=localhost',
    `WEBSOCKET_URL=ws://localhost:${values.CANVAS_PORT || '3000'}/ws`,
    '',
    '# ============================================',
    '# Workspace Configuration',
    '# ============================================',
    `WORKSPACE_PATH=${values.WORKSPACE_PATH || '~/10x-skill-workspace'}`,
    '',
    '# ============================================',
    '# Logging & Debug',
    '# ============================================',
    `DEBUG=${values.DEBUG || 'false'}`,
    'LOG_LEVEL=info',
    ''
  );

  return lines.join('\n');
}

// Display configuration summary
function displaySummary(values) {
  log.header('\n═══ CONFIGURATION SUMMARY ═══\n');

  // Required features
  log.section('Required Features:');
  log.success('Prospect enrichment (Exa AI)');
  log.success('Gmail integration');
  log.success('Email campaigns');

  // Optional features
  const optionalFeatures = [];
  if (values.GEMINI_API_KEY) optionalFeatures.push('Multimodal features (Gemini AI)');
  if (values.CANVA_CLIENT_ID) optionalFeatures.push('Design automation (Canva)');
  if (values.ANTHROPIC_API_KEY) optionalFeatures.push('Advanced AI features (Claude API)');

  if (optionalFeatures.length > 0) {
    log.section('\nOptional Features Enabled:');
    optionalFeatures.forEach((feature) => log.success(feature));
  }

  // Disabled features
  const disabledFeatures = [];
  if (!values.GEMINI_API_KEY) disabledFeatures.push('Multimodal features (no Gemini API key)');
  if (!values.CANVA_CLIENT_ID) disabledFeatures.push('Design automation (no Canva credentials)');

  if (disabledFeatures.length > 0) {
    log.section('\nDisabled Features:');
    disabledFeatures.forEach((feature) => log.warning(feature));
  }

  // Workspace
  log.section('\nWorkspace:');
  console.log(`  Path: ${values.WORKSPACE_PATH}`);
  console.log(`  Canvas Port: ${values.CANVAS_PORT}`);
  console.log(`  Debug Mode: ${values.DEBUG}`);
}

// Create workspace directories
async function createWorkspace(workspacePath) {
  try {
    const expandedPath = workspacePath.replace('~', process.env.HOME || process.env.USERPROFILE);
    const dirs = [
      expandedPath,
      path.join(expandedPath, 'campaigns'),
      path.join(expandedPath, 'templates'),
      path.join(expandedPath, 'outputs'),
      path.join(expandedPath, 'logs'),
    ];

    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }

    log.success(`Workspace created at: ${expandedPath}`);
  } catch (error) {
    log.error(`Failed to create workspace: ${error.message}`);
  }
}

// Display next steps
function displayNextSteps() {
  log.header('\n═══ NEXT STEPS ═══\n');

  console.log(`${colors.bright}1. Load the Browser Extension:${colors.reset}`);
  log.dim('   - Open Chrome/Edge');
  log.dim('   - Go to chrome://extensions/');
  log.dim('   - Enable "Developer mode"');
  log.dim('   - Click "Load unpacked"');
  log.dim('   - Select: browser-extension/');

  console.log(`\n${colors.bright}2. Start the Canvas Server:${colors.reset}`);
  log.dim('   cd tldraw-canvas');
  log.dim('   npm run dev -- --port 3000');

  console.log(`\n${colors.bright}3. Open the Visual Canvas:${colors.reset}`);
  log.dim('   http://localhost:3000');

  console.log(`\n${colors.bright}4. Use Claude Code:${colors.reset}`);
  log.dim('   Say: "start my app" or "/start"');

  console.log(`\n${colors.bright}Available Commands:${colors.reset}`);
  log.dim('   /start      - Start the visual canvas');
  log.dim('   /discover   - Find people using Exa AI');
  log.dim('   /outreach   - Email campaigns');
  log.dim('   /linkedin   - LinkedIn automation');
  log.dim('   /twitter    - Twitter automation');
  log.dim('   /instagram  - Instagram automation');
  log.dim('   /workflow   - Multi-platform sequences');

  console.log('');
}

// Main setup flow
async function main() {
  try {
    displayBanner();

    log.info('This setup wizard will guide you through configuring your environment.');
    log.info('Press Ctrl+C at any time to cancel.\n');

    await question('Press Enter to continue...');

    // Collect configuration
    const values = await collectConfig();

    // Display summary
    displaySummary(values);

    // Confirm
    console.log('');
    const confirm = await question(
      `${colors.yellow}Save this configuration to .env? (y/n):${colors.reset} `
    );

    if (confirm.toLowerCase() !== 'y') {
      log.warning('Setup cancelled. No files were modified.');
      rl.close();
      return;
    }

    // Generate and save .env file
    const envContent = generateEnvContent(values);
    const envPath = path.join(__dirname, '.env');

    // Backup existing .env if it exists
    if (fs.existsSync(envPath)) {
      const backupPath = path.join(__dirname, `.env.backup.${Date.now()}`);
      fs.copyFileSync(envPath, backupPath);
      log.info(`Existing .env backed up to: ${path.basename(backupPath)}`);
    }

    fs.writeFileSync(envPath, envContent);
    log.success('.env file created successfully!');

    // Create workspace directories
    await createWorkspace(values.WORKSPACE_PATH);

    // Display next steps
    displayNextSteps();

    log.success('\n✨ Setup complete! You\'re ready to start using 10x-Outreach-Skill!');

    rl.close();
  } catch (error) {
    log.error(`Setup failed: ${error.message}`);
    rl.close();
    process.exit(1);
  }
}

// Handle cleanup
rl.on('close', () => {
  console.log('');
  process.exit(0);
});

// Run setup
main();
