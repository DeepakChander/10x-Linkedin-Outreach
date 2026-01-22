#!/usr/bin/env node

/**
 * LinkedIn Lookback Prospect Enrichment Script
 *
 * Enriches prospect data using Exa AI discovery and other data sources.
 *
 * Usage:
 *   node enrich-prospects.js --url <linkedin_url>
 *   node enrich-prospects.js --recent 7d
 *   node enrich-prospects.js --all
 *
 * Options:
 *   --url URL        Enrich specific LinkedIn profile URL
 *   --recent PERIOD  Enrich recent profiles (e.g., 7d, 30d, 1w, 1m)
 *   --all            Enrich all profiles in database
 *   --output FILE    Save enriched data to JSON file
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
  EXA_API_KEY: process.env.EXA_API_KEY,
  DATA_DIR: path.join(__dirname, '../../../data/linkedin-lookback'),
  DB_FILE: path.join(__dirname, '../../../data/linkedin-lookback/lookback-database.json'),
  OUTPUT_DIR: path.join(__dirname, '../../../data/linkedin-lookback/enriched'),
  LOG_FILE: path.join(__dirname, '../../../data/linkedin-lookback/enrich.log')
};

// Ensure directories exist
[CONFIG.DATA_DIR, CONFIG.OUTPUT_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Logging
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
    url: null,
    recent: null,
    all: false,
    output: null
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--url':
        options.url = args[++i];
        break;
      case '--recent':
        options.recent = args[++i];
        break;
      case '--all':
        options.all = true;
        break;
      case '--output':
        options.output = args[++i];
        break;
    }
  }

  return options;
}

// Load database
function loadDatabase() {
  if (!fs.existsSync(CONFIG.DB_FILE)) {
    log('Database not found. Run sync-lookback-data.js first', 'ERROR');
    return null;
  }
  return JSON.parse(fs.readFileSync(CONFIG.DB_FILE, 'utf8'));
}

// Save database
function saveDatabase(data) {
  fs.writeFileSync(CONFIG.DB_FILE, JSON.stringify(data, null, 2));
}

// Parse time period (e.g., "7d", "30d", "1w", "1m")
function parsePeriod(period) {
  const match = period.match(/^(\d+)([dwm])$/);
  if (!match) return null;

  const value = parseInt(match[1]);
  const unit = match[2];

  const now = new Date();
  switch (unit) {
    case 'd':
      now.setDate(now.getDate() - value);
      break;
    case 'w':
      now.setDate(now.getDate() - (value * 7));
      break;
    case 'm':
      now.setMonth(now.getMonth() - value);
      break;
  }

  return now.toISOString();
}

// Get profiles to enrich
function getProfilesToEnrich(db, options) {
  let profiles = [];

  if (options.url) {
    // Single profile
    const profile = db.prospects.find(p => p.linkedin_url === options.url);
    if (profile) {
      profiles = [profile];
    } else {
      log(`Profile not found: ${options.url}`, 'WARN');
    }
  } else if (options.recent) {
    // Recent profiles
    const sinceDate = parsePeriod(options.recent);
    if (!sinceDate) {
      log(`Invalid period format: ${options.recent}`, 'ERROR');
      return [];
    }

    profiles = db.activities
      .filter(a => new Date(a.timestamp) >= new Date(sinceDate))
      .map(a => a.linkedin_url)
      .filter((url, index, self) => url && self.indexOf(url) === index) // Unique URLs
      .map(url => {
        let prospect = db.prospects.find(p => p.linkedin_url === url);
        if (!prospect) {
          // Create prospect from activity data
          const activity = db.activities.find(a => a.linkedin_url === url);
          prospect = {
            linkedin_url: url,
            first_name: activity.profile_name?.split(' ')[0] || '',
            last_name: activity.profile_name?.split(' ').slice(1).join(' ') || '',
            full_name: activity.profile_name,
            company: activity.company || '',
            current_title: activity.current_title || '',
            location: activity.location || ''
          };
        }
        return prospect;
      });
  } else if (options.all) {
    // All profiles
    profiles = db.prospects || [];

    // Also include profiles from activities that aren't in prospects
    const prospectUrls = new Set(profiles.map(p => p.linkedin_url));
    db.activities.forEach(activity => {
      if (activity.linkedin_url && !prospectUrls.has(activity.linkedin_url)) {
        profiles.push({
          linkedin_url: activity.linkedin_url,
          first_name: activity.profile_name?.split(' ')[0] || '',
          last_name: activity.profile_name?.split(' ').slice(1).join(' ') || '',
          full_name: activity.profile_name,
          company: activity.company || '',
          current_title: activity.current_title || '',
          location: activity.location || ''
        });
        prospectUrls.add(activity.linkedin_url);
      }
    });
  }

  log(`Found ${profiles.length} profiles to enrich`);
  return profiles;
}

// Call Exa AI API
async function callExaAPI(query, options = {}) {
  if (!CONFIG.EXA_API_KEY) {
    log('EXA_API_KEY not set in environment', 'ERROR');
    throw new Error('EXA_API_KEY required for enrichment');
  }

  const payload = {
    query,
    type: options.type || 'neural',
    num_results: options.num_results || 10,
    contents: {
      text: true,
      highlights: true
    }
  };

  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);
    const req = https.request({
      hostname: 'api.exa.ai',
      path: '/search',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': CONFIG.EXA_API_KEY,
        'Content-Length': data.length
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Failed to parse Exa API response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Extract company information
async function enrichCompanyData(companyName) {
  if (!companyName) return null;

  log(`Enriching company: ${companyName}`);

  try {
    const results = await callExaAPI(`${companyName} company information tech stack funding`, {
      num_results: 5
    });

    const companyData = {
      name: companyName,
      tech_stack: extractTechStack(results),
      funding_info: extractFundingInfo(results),
      company_size: extractCompanySize(results),
      recent_news: extractRecentNews(results),
      website: extractWebsite(results)
    };

    return companyData;
  } catch (error) {
    log(`Error enriching company ${companyName}: ${error.message}`, 'ERROR');
    return null;
  }
}

// Extract tech stack from search results
function extractTechStack(results) {
  // Common tech keywords to look for
  const techKeywords = [
    'React', 'Vue', 'Angular', 'Node.js', 'Python', 'Django', 'Flask',
    'AWS', 'Google Cloud', 'Azure', 'Docker', 'Kubernetes',
    'PostgreSQL', 'MongoDB', 'MySQL', 'Redis',
    'Salesforce', 'HubSpot', 'Stripe', 'Twilio'
  ];

  const found = new Set();
  const text = results.results?.map(r => r.text).join(' ') || '';

  techKeywords.forEach(tech => {
    if (text.toLowerCase().includes(tech.toLowerCase())) {
      found.add(tech);
    }
  });

  return Array.from(found);
}

// Extract funding information
function extractFundingInfo(results) {
  const text = results.results?.map(r => r.text).join(' ') || '';
  const fundingPattern = /\$\d+(\.\d+)?[BMK]|Series [A-F]|seed round|raised \$|funding/gi;
  const matches = text.match(fundingPattern);
  return matches ? [...new Set(matches)].slice(0, 5) : [];
}

// Extract company size
function extractCompanySize(results) {
  const text = results.results?.map(r => r.text).join(' ') || '';
  const sizePattern = /(\d+[\+\-]?)\s*employees?/gi;
  const matches = text.match(sizePattern);
  return matches ? matches[0] : null;
}

// Extract recent news
function extractRecentNews(results) {
  return results.results?.slice(0, 3).map(r => ({
    title: r.title,
    url: r.url,
    snippet: r.highlights?.[0] || r.text?.substring(0, 200)
  })) || [];
}

// Extract website
function extractWebsite(results) {
  const url = results.results?.[0]?.url;
  if (!url) return null;

  try {
    const parsed = new URL(url);
    return parsed.origin;
  } catch (e) {
    return null;
  }
}

// Find social profiles
async function findSocialProfiles(name, company) {
  const profiles = {
    github: null,
    twitter: null,
    personal_website: null
  };

  try {
    // Search for GitHub
    const githubResults = await callExaAPI(`${name} ${company} site:github.com`, {
      num_results: 3
    });
    profiles.github = githubResults.results?.find(r => r.url.includes('github.com'))?.url || null;

    // Search for Twitter
    const twitterResults = await callExaAPI(`${name} ${company} site:twitter.com OR site:x.com`, {
      num_results: 3
    });
    profiles.twitter = twitterResults.results?.find(r =>
      r.url.includes('twitter.com') || r.url.includes('x.com')
    )?.url || null;

    // Search for personal website
    const websiteResults = await callExaAPI(`${name} personal website blog portfolio`, {
      num_results: 5
    });
    const personalDomains = websiteResults.results?.filter(r =>
      !r.url.includes('linkedin.com') &&
      !r.url.includes('twitter.com') &&
      !r.url.includes('facebook.com') &&
      !r.url.includes('github.com')
    );
    profiles.personal_website = personalDomains?.[0]?.url || null;

  } catch (error) {
    log(`Error finding social profiles: ${error.message}`, 'WARN');
  }

  return profiles;
}

// Enrich single profile
async function enrichProfile(profile) {
  log(`Enriching: ${profile.full_name || profile.linkedin_url}`);

  const enrichedData = {
    enriched_at: new Date().toISOString()
  };

  try {
    // Enrich company data
    if (profile.company) {
      const companyData = await enrichCompanyData(profile.company);
      if (companyData) {
        enrichedData.company_data = companyData;
      }
    }

    // Find social profiles
    if (profile.full_name) {
      const socialProfiles = await findSocialProfiles(profile.full_name, profile.company);
      enrichedData.social_profiles = socialProfiles;
    }

    // Generate personalization hooks
    enrichedData.personalization_hooks = generatePersonalizationHooks(profile, enrichedData);

    log(`Successfully enriched: ${profile.full_name || profile.linkedin_url}`);
    return {
      ...profile,
      enriched_data: enrichedData
    };

  } catch (error) {
    log(`Error enriching ${profile.linkedin_url}: ${error.message}`, 'ERROR');
    return profile; // Return original if enrichment fails
  }
}

// Generate personalization hooks for outreach
function generatePersonalizationHooks(profile, enrichedData) {
  const hooks = [];

  // Company tech stack
  if (enrichedData.company_data?.tech_stack?.length > 0) {
    hooks.push({
      type: 'tech_stack',
      text: `I noticed ${profile.company} uses ${enrichedData.company_data.tech_stack.slice(0, 2).join(' and ')}`
    });
  }

  // Company funding
  if (enrichedData.company_data?.funding_info?.length > 0) {
    hooks.push({
      type: 'funding',
      text: `Congrats on ${profile.company}'s recent funding ${enrichedData.company_data.funding_info[0]}`
    });
  }

  // Recent news
  if (enrichedData.company_data?.recent_news?.length > 0) {
    hooks.push({
      type: 'news',
      text: `I saw that ${profile.company} ${enrichedData.company_data.recent_news[0].snippet}`,
      source: enrichedData.company_data.recent_news[0].url
    });
  }

  // Personal content
  if (enrichedData.social_profiles?.github) {
    hooks.push({
      type: 'github',
      text: `I saw your work on GitHub - particularly impressed by your contributions`
    });
  }

  return hooks;
}

// Main execution
async function main() {
  const options = parseArgs();

  log('=== LinkedIn Lookback Prospect Enrichment Started ===');

  try {
    // Load database
    const db = loadDatabase();
    if (!db) {
      process.exit(1);
    }

    // Get profiles to enrich
    const profiles = getProfilesToEnrich(db, options);
    if (profiles.length === 0) {
      log('No profiles to enrich', 'WARN');
      process.exit(0);
    }

    // Enrich profiles (with rate limiting)
    const enriched = [];
    for (let i = 0; i < profiles.length; i++) {
      const profile = profiles[i];
      log(`Processing ${i + 1}/${profiles.length}: ${profile.full_name || profile.linkedin_url}`);

      const enrichedProfile = await enrichProfile(profile);
      enriched.push(enrichedProfile);

      // Rate limit: wait 2 seconds between requests
      if (i < profiles.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    // Update database
    enriched.forEach(enrichedProfile => {
      const index = db.prospects.findIndex(p => p.linkedin_url === enrichedProfile.linkedin_url);
      if (index >= 0) {
        db.prospects[index] = enrichedProfile;
      } else {
        db.prospects.push(enrichedProfile);
      }
    });

    saveDatabase(db);
    log(`Database updated with ${enriched.length} enriched profiles`);

    // Save enriched data to output file if specified
    if (options.output) {
      const outputPath = path.join(CONFIG.OUTPUT_DIR, options.output);
      fs.writeFileSync(outputPath, JSON.stringify(enriched, null, 2));
      log(`Enriched data saved to: ${outputPath}`);
    }

    log('=== Enrichment Complete ===');
    log(`Summary: Enriched ${enriched.length} profiles`);

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
  enrichProfile,
  enrichCompanyData,
  findSocialProfiles,
  generatePersonalizationHooks
};
