#!/usr/bin/env node

/**
 * LinkedIn Lookback Data Sync Script
 *
 * Exports activity data from LinkedIn Lookback extension IndexedDB
 * and imports into 10x-Team database for workflow automation.
 *
 * Usage:
 *   node sync-lookback-data.js [--profile-path PATH]
 *
 * Options:
 *   --profile-path   Path to Chrome profile directory (auto-detected if not provided)
 *   --export-only    Only export data to JSON, don't import to database
 *   --since          Sync activities since date (ISO format: 2026-01-01)
 *   --dry-run        Preview what would be synced without making changes
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const CONFIG = {
  DB_NAME: 'LinkedInActivityTracker',
  DB_VERSION: 1,
  STORES: {
    ACTIVITIES: 'activities',
    PROSPECTS: 'prospects',
    SETTINGS: 'settings'
  },
  OUTPUT_DIR: path.join(__dirname, '../../../data/linkedin-lookback'),
  LOG_FILE: path.join(__dirname, '../../../data/linkedin-lookback/sync.log')
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.OUTPUT_DIR)) {
  fs.mkdirSync(CONFIG.OUTPUT_DIR, { recursive: true });
}

// Logging utility
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] ${message}`;
  console.log(logMessage);
  fs.appendFileSync(CONFIG.LOG_FILE, logMessage + '\n');
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    profilePath: null,
    exportOnly: false,
    since: null,
    dryRun: false
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--profile-path':
        options.profilePath = args[++i];
        break;
      case '--export-only':
        options.exportOnly = true;
        break;
      case '--since':
        options.since = args[++i];
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
    }
  }

  return options;
}

// Detect Chrome profile path
function detectChromeProfilePath() {
  const platform = os.platform();
  const homeDir = os.homedir();

  const paths = {
    darwin: path.join(homeDir, 'Library/Application Support/Google/Chrome/Default'),
    win32: path.join(homeDir, 'AppData/Local/Google/Chrome/User Data/Default'),
    linux: path.join(homeDir, '.config/google-chrome/default')
  };

  return paths[platform] || null;
}

// Export data from IndexedDB
async function exportFromIndexedDB(profilePath) {
  log('Exporting data from LinkedIn Lookback extension...');

  // Note: Direct IndexedDB access from Node.js requires browser automation
  // We'll use Puppeteer to access the extension's IndexedDB

  const puppeteer = require('puppeteer');

  log(`Using Chrome profile: ${profilePath}`);

  const browser = await puppeteer.launch({
    headless: false, // Must be false to access extension data
    userDataDir: profilePath,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  try {
    const page = await browser.newPage();

    // Navigate to a page where we can execute our extraction script
    await page.goto('chrome://extensions/');

    // Execute script to extract data from IndexedDB
    const data = await page.evaluate(async (config) => {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open(config.DB_NAME, config.DB_VERSION);

        request.onerror = () => reject(request.error);

        request.onsuccess = () => {
          const db = request.result;
          const result = {
            activities: [],
            prospects: [],
            settings: {}
          };

          // Read activities
          const activitiesTransaction = db.transaction([config.STORES.ACTIVITIES], 'readonly');
          const activitiesStore = activitiesTransaction.objectStore(config.STORES.ACTIVITIES);
          const activitiesRequest = activitiesStore.getAll();

          activitiesRequest.onsuccess = () => {
            result.activities = activitiesRequest.result;

            // Read prospects
            const prospectsTransaction = db.transaction([config.STORES.PROSPECTS], 'readonly');
            const prospectsStore = prospectsTransaction.objectStore(config.STORES.PROSPECTS);
            const prospectsRequest = prospectsStore.getAll();

            prospectsRequest.onsuccess = () => {
              result.prospects = prospectsRequest.result;

              // Read settings
              const settingsTransaction = db.transaction([config.STORES.SETTINGS], 'readonly');
              const settingsStore = settingsTransaction.objectStore(config.STORES.SETTINGS);
              const settingsRequest = settingsStore.getAll();

              settingsRequest.onsuccess = () => {
                result.settings = settingsRequest.result.reduce((acc, item) => {
                  acc[item.key] = item.value;
                  return acc;
                }, {});

                resolve(result);
              };
            };
          };
        };
      });
    }, CONFIG);

    await browser.close();
    return data;

  } catch (error) {
    await browser.close();
    throw error;
  }
}

// Simpler approach: Use Chrome Extension Message Passing
// This requires a helper extension or script injected into the page
async function exportViaExtensionAPI() {
  log('Attempting export via Extension API...');

  // This is a placeholder - actual implementation would depend on
  // modifying the LinkedIn Lookback extension to expose an export API

  log('Note: Direct IndexedDB access requires browser automation.');
  log('Alternative: Export manually from extension popup and use --import flag');

  return null;
}

// Export activities to JSON file
function saveToJSON(data, filename = null) {
  if (!filename) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    filename = `linkedin-lookback-export-${timestamp}.json`;
  }

  const filepath = path.join(CONFIG.OUTPUT_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
  log(`Data exported to: ${filepath}`);
  return filepath;
}

// Import data from JSON file
function importFromJSON(filepath) {
  log(`Importing data from: ${filepath}`);
  const content = fs.readFileSync(filepath, 'utf8');
  return JSON.parse(content);
}

// Filter activities by date
function filterActivitiesByDate(activities, sinceDate) {
  if (!sinceDate) return activities;

  const cutoffDate = new Date(sinceDate);
  return activities.filter(activity => {
    const activityDate = new Date(activity.timestamp);
    return activityDate >= cutoffDate;
  });
}

// Transform data for 10x-Team database format
function transformData(data, options = {}) {
  log('Transforming data for 10x-Team format...');

  let activities = data.activities || [];

  // Filter by date if specified
  if (options.since) {
    const beforeCount = activities.length;
    activities = filterActivitiesByDate(activities, options.since);
    log(`Filtered ${beforeCount - activities.length} activities before ${options.since}`);
  }

  // Add metadata
  const transformed = {
    sync_timestamp: new Date().toISOString(),
    source: 'linkedin-lookback',
    version: '1.0.0',
    stats: {
      total_activities: activities.length,
      profile_views: activities.filter(a => a.activity_type === 'profile_view').length,
      connection_requests: activities.filter(a => a.activity_type === 'connection_request').length,
      messages_sent: activities.filter(a => a.activity_type === 'message_sent').length,
      known_prospects: activities.filter(a => a.is_known_prospect).length
    },
    activities: activities.map(activity => ({
      ...activity,
      synced_at: new Date().toISOString(),
      source: 'linkedin-lookback'
    })),
    prospects: (data.prospects || []).map(prospect => ({
      ...prospect,
      synced_at: new Date().toISOString(),
      source: 'linkedin-lookback'
    })),
    settings: data.settings || {}
  };

  log(`Transformed ${transformed.activities.length} activities and ${transformed.prospects.length} prospects`);
  return transformed;
}

// Save to 10x-Team database
async function saveTo10xTeamDB(data, dryRun = false) {
  if (dryRun) {
    log('[DRY RUN] Would save to database:', 'WARN');
    log(`  - ${data.activities.length} activities`);
    log(`  - ${data.prospects.length} prospects`);
    return { success: true, dryRun: true };
  }

  log('Saving to 10x-Team database...');

  // This would connect to your actual database
  // For now, we'll save to a local JSON file as a proxy

  const dbFile = path.join(CONFIG.OUTPUT_DIR, 'lookback-database.json');
  let existingData = { activities: [], prospects: [] };

  if (fs.existsSync(dbFile)) {
    existingData = JSON.parse(fs.readFileSync(dbFile, 'utf8'));
  }

  // Merge activities (avoid duplicates by ID)
  const existingActivityIds = new Set(existingData.activities.map(a => a.id));
  const newActivities = data.activities.filter(a => !existingActivityIds.has(a.id));
  existingData.activities.push(...newActivities);

  // Merge prospects (avoid duplicates by linkedin_url)
  const existingProspectUrls = new Set(existingData.prospects.map(p => p.linkedin_url));
  const newProspects = data.prospects.filter(p => !existingProspectUrls.has(p.linkedin_url));
  existingData.prospects.push(...newProspects);

  fs.writeFileSync(dbFile, JSON.stringify(existingData, null, 2));

  log(`Saved ${newActivities.length} new activities and ${newProspects.length} new prospects`);
  log(`Total database now has ${existingData.activities.length} activities and ${existingData.prospects.length} prospects`);

  return {
    success: true,
    added: {
      activities: newActivities.length,
      prospects: newProspects.length
    },
    total: {
      activities: existingData.activities.length,
      prospects: existingData.prospects.length
    }
  };
}

// Trigger automation workflows
async function triggerWorkflows(data, dryRun = false) {
  if (dryRun) {
    log('[DRY RUN] Would trigger workflows:', 'WARN');
    return;
  }

  log('Analyzing activities for workflow triggers...');

  const triggers = {
    new_warm_leads: [],
    pending_follow_ups: [],
    connection_accepted: [],
    no_reply_escalation: []
  };

  // Identify warm leads (multiple profile views)
  const profileViewCounts = {};
  data.activities
    .filter(a => a.activity_type === 'profile_view')
    .forEach(a => {
      profileViewCounts[a.linkedin_url] = (profileViewCounts[a.linkedin_url] || 0) + 1;
    });

  Object.entries(profileViewCounts).forEach(([url, count]) => {
    if (count >= 3) {
      triggers.new_warm_leads.push({ url, view_count: count });
    }
  });

  log(`Identified ${triggers.new_warm_leads.length} warm leads`);

  // TODO: Implement additional workflow triggers
  // - Connection requests pending follow-up
  // - Messages sent without replies
  // - Accepted connections needing intro message

  return triggers;
}

// Main execution
async function main() {
  const options = parseArgs();

  log('=== LinkedIn Lookback Data Sync Started ===');
  log(`Options: ${JSON.stringify(options)}`);

  try {
    let data;

    // Check if we should import from existing export
    const exportFiles = fs.readdirSync(CONFIG.OUTPUT_DIR)
      .filter(f => f.startsWith('linkedin-lookback-export') && f.endsWith('.json'))
      .sort()
      .reverse();

    if (exportFiles.length > 0 && !options.profilePath) {
      log(`Found existing export: ${exportFiles[0]}`);
      log('Using this export. To create a new export, specify --profile-path');
      data = importFromJSON(path.join(CONFIG.OUTPUT_DIR, exportFiles[0]));
    } else {
      // Detect or use provided Chrome profile path
      const profilePath = options.profilePath || detectChromeProfilePath();

      if (!profilePath) {
        throw new Error('Could not detect Chrome profile path. Please specify with --profile-path');
      }

      // Export from IndexedDB
      log('Note: Automated export requires Puppeteer and browser access');
      log('For manual export: Open extension popup → Export to CSV → use that file');

      // For now, provide instructions
      log('');
      log('MANUAL EXPORT INSTRUCTIONS:', 'WARN');
      log('1. Open LinkedIn Lookback extension popup');
      log('2. Go to Activity tab');
      log('3. Click "Export Activities" button');
      log('4. Save CSV to: ' + CONFIG.OUTPUT_DIR);
      log('5. Re-run this script');
      log('');

      throw new Error('Manual export required - see instructions above');
    }

    // Transform data
    const transformed = transformData(data, options);

    // Save export
    if (options.exportOnly) {
      const filepath = saveToJSON(transformed);
      log(`Export complete: ${filepath}`);
      log('=== Sync Complete (Export Only) ===');
      return;
    }

    // Save to database
    const dbResult = await saveTo10xTeamDB(transformed, options.dryRun);
    log(`Database update: ${JSON.stringify(dbResult)}`);

    // Trigger workflows
    const triggers = await triggerWorkflows(transformed, options.dryRun);
    log(`Workflow triggers: ${JSON.stringify(triggers)}`);

    log('=== Sync Complete ===');
    log(`Summary: Synced ${transformed.stats.total_activities} activities, ${triggers.new_warm_leads.length} warm leads identified`);

  } catch (error) {
    log(`Error: ${error.message}`, 'ERROR');
    log(error.stack, 'ERROR');
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  exportFromIndexedDB,
  exportViaExtensionAPI,
  saveToJSON,
  importFromJSON,
  transformData,
  saveTo10xTeamDB,
  triggerWorkflows
};
