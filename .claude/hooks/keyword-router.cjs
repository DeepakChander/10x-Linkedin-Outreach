#!/usr/bin/env node
'use strict';

/**
 * Keyword Router - Intelligent routing based on user intent keywords
 *
 * Routes user requests to appropriate skills/tools based on detected keywords
 * and context. Works as a pre-processing hook to optimize skill selection.
 *
 * Features:
 * - Multi-keyword detection with priority scoring
 * - Context-aware routing (considers conversation history)
 * - MCP tool preference hints
 * - Fallback handling for ambiguous requests
 *
 * @module keyword-router
 */

const fs = require('fs');
const path = require('path');

// Keyword mappings with priority scores (higher = more specific)
const KEYWORD_ROUTES = {
  // Discovery & Research
  'discover': { skill: 'discovery-engine', priority: 10, mcp: 'exa' },
  'find people': { skill: 'discovery-engine', priority: 9, mcp: 'exa' },
  'search for': { skill: 'discovery-engine', priority: 7, mcp: 'exa' },
  'lookup': { skill: 'discovery-engine', priority: 6, mcp: 'exa' },
  'research': { skill: 'discovery-engine', priority: 5, mcp: 'exa' },
  'webset': { skill: 'discovery-engine', priority: 10, mcp: 'exa-websets' },

  // Email Operations
  'send email': { skill: 'email-composer', priority: 10, mcp: 'gmail' },
  'compose email': { skill: 'email-composer', priority: 10, mcp: 'gmail' },
  'write email': { skill: 'email-composer', priority: 9, mcp: 'gmail' },
  'email campaign': { skill: 'outreach-manager', priority: 10, mcp: 'gmail' },
  'cold email': { skill: 'outreach-manager', priority: 10, mcp: 'gmail' },
  'bulk email': { skill: 'outreach-manager', priority: 10, mcp: 'gmail' },
  'outreach': { skill: 'outreach-manager', priority: 8, mcp: 'gmail' },

  // Inbox Operations
  'check inbox': { skill: 'inbox-reader', priority: 10, mcp: 'gmail' },
  'read emails': { skill: 'inbox-reader', priority: 9, mcp: 'gmail' },
  'inbox': { skill: 'inbox-reader', priority: 8, mcp: 'gmail' },
  'my emails': { skill: 'inbox-reader', priority: 7, mcp: 'gmail' },

  // Reply Operations
  'reply to': { skill: 'reply-generator', priority: 10, mcp: 'gmail' },
  'respond to': { skill: 'reply-generator', priority: 9, mcp: 'gmail' },

  // Summarization
  'summarize': { skill: 'email-summarizer', priority: 10, mcp: 'gmail' },
  'digest': { skill: 'email-summarizer', priority: 9, mcp: 'gmail' },
  'summary': { skill: 'email-summarizer', priority: 8, mcp: 'gmail' },

  // LinkedIn Operations
  'linkedin': { skill: 'linkedin-adapter', priority: 8, mcp: 'browser-use' },
  'connect on linkedin': { skill: 'linkedin-adapter', priority: 10, mcp: 'browser-use' },
  'linkedin message': { skill: 'linkedin-adapter', priority: 10, mcp: 'browser-use' },
  'linkedin dm': { skill: 'linkedin-adapter', priority: 10, mcp: 'browser-use' },

  // Twitter Operations
  'twitter': { skill: 'twitter-adapter', priority: 8, mcp: 'browser-use' },
  'tweet': { skill: 'twitter-adapter', priority: 9, mcp: 'browser-use' },
  'twitter dm': { skill: 'twitter-adapter', priority: 10, mcp: 'browser-use' },
  'follow on twitter': { skill: 'twitter-adapter', priority: 10, mcp: 'browser-use' },

  // Instagram Operations
  'instagram': { skill: 'instagram-adapter', priority: 8, mcp: 'browser-use' },
  'instagram dm': { skill: 'instagram-adapter', priority: 10, mcp: 'browser-use' },
  'ig dm': { skill: 'instagram-adapter', priority: 10, mcp: 'browser-use' },

  // Workflow Operations
  'workflow': { skill: 'workflow-engine', priority: 8, mcp: null },
  'create workflow': { skill: 'workflow-engine', priority: 10, mcp: null },
  'run workflow': { skill: 'workflow-engine', priority: 10, mcp: null },
  'campaign': { skill: 'workflow-engine', priority: 7, mcp: null },

  // Canvas Operations
  'canvas': { skill: 'canvas-workflow', priority: 9, mcp: null },
  'visual': { skill: 'canvas-workflow', priority: 6, mcp: null },
  'design workflow': { skill: 'canvas-workflow', priority: 10, mcp: null },

  // Team Operations
  'team': { skill: 'team-manager', priority: 8, mcp: null },
  'add team member': { skill: 'team-manager', priority: 10, mcp: null },
  'team credentials': { skill: 'team-manager', priority: 10, mcp: null },

  // Template Operations
  'template': { skill: 'template-manager', priority: 8, mcp: null },
  'create template': { skill: 'template-manager', priority: 10, mcp: null },
  'edit template': { skill: 'template-manager', priority: 10, mcp: null },

  // Analytics Operations
  'analytics': { skill: 'analytics', priority: 9, mcp: null },
  'metrics': { skill: 'analytics', priority: 8, mcp: null },
  'performance': { skill: 'analytics', priority: 7, mcp: null },
  'statistics': { skill: 'analytics', priority: 7, mcp: null },
  'report': { skill: 'analytics', priority: 6, mcp: null },

  // Content Marketing Operations
  'content': { skill: 'content-marketing', priority: 7, mcp: 'exa' },
  'blog post': { skill: 'content-marketing', priority: 10, mcp: 'exa' },
  'article': { skill: 'content-marketing', priority: 8, mcp: 'exa' },
  'content calendar': { skill: 'content-marketing', priority: 10, mcp: null },
  'social post': { skill: 'content-marketing', priority: 9, mcp: null },

  // SEO Operations
  'seo': { skill: 'seo-optimization', priority: 10, mcp: 'exa' },
  'keyword research': { skill: 'seo-optimization', priority: 10, mcp: 'exa' },
  'optimize': { skill: 'seo-optimization', priority: 6, mcp: 'exa' },
  'ranking': { skill: 'seo-optimization', priority: 8, mcp: 'exa' },
  'backlinks': { skill: 'seo-optimization', priority: 9, mcp: 'exa' }
};

// Context modifiers that influence routing
const CONTEXT_MODIFIERS = {
  'multiple': { boost: 'outreach-manager', amount: 3 },
  'bulk': { boost: 'outreach-manager', amount: 3 },
  'batch': { boost: 'outreach-manager', amount: 3 },
  'single': { boost: 'email-composer', amount: 3 },
  'one': { boost: 'email-composer', amount: 2 },
  'automated': { boost: 'workflow-engine', amount: 3 },
  'sequence': { boost: 'workflow-engine', amount: 3 },
  'schedule': { boost: 'workflow-engine', amount: 2 }
};

/**
 * Detect keywords in user input and return routing suggestions
 * @param {string} input - User input text
 * @returns {Object} Routing result with skill, mcp, and confidence
 */
function detectKeywords(input) {
  const normalizedInput = input.toLowerCase().trim();
  const matches = [];

  // Check all keyword routes
  for (const [keyword, route] of Object.entries(KEYWORD_ROUTES)) {
    if (normalizedInput.includes(keyword)) {
      matches.push({
        keyword,
        ...route,
        score: route.priority
      });
    }
  }

  // Apply context modifiers
  for (const [modifier, config] of Object.entries(CONTEXT_MODIFIERS)) {
    if (normalizedInput.includes(modifier)) {
      matches.forEach(match => {
        if (match.skill === config.boost) {
          match.score += config.amount;
        }
      });
    }
  }

  // Sort by score (highest first)
  matches.sort((a, b) => b.score - a.score);

  if (matches.length === 0) {
    return {
      skill: null,
      mcp: null,
      confidence: 0,
      alternatives: [],
      reason: 'No keywords matched'
    };
  }

  const best = matches[0];
  const alternatives = matches.slice(1, 4).map(m => ({
    skill: m.skill,
    mcp: m.mcp,
    keyword: m.keyword
  }));

  // Calculate confidence based on score and specificity
  const confidence = Math.min(100, best.score * 10);

  return {
    skill: best.skill,
    mcp: best.mcp,
    confidence,
    keyword: best.keyword,
    alternatives,
    reason: `Matched keyword: "${best.keyword}" with priority ${best.priority}`
  };
}

/**
 * Get MCP tool recommendation for a skill
 * @param {string} skill - Skill name
 * @returns {Object} MCP configuration hints
 */
function getMCPRecommendation(skill) {
  const mcpMap = {
    'discovery-engine': {
      primary: 'exa',
      fallback: 'browser-use',
      reason: 'Exa provides semantic search for people discovery'
    },
    'outreach-manager': {
      primary: 'gmail',
      fallback: null,
      reason: 'Gmail API for sending campaign emails'
    },
    'linkedin-adapter': {
      primary: 'browser-use',
      fallback: null,
      reason: 'Browser automation for LinkedIn actions'
    },
    'twitter-adapter': {
      primary: 'browser-use',
      fallback: null,
      reason: 'Browser automation for Twitter actions'
    },
    'instagram-adapter': {
      primary: 'browser-use',
      fallback: null,
      reason: 'Browser automation for Instagram actions'
    },
    'seo-optimization': {
      primary: 'exa',
      fallback: 'browser-use',
      reason: 'Exa for keyword research and competitor analysis'
    },
    'content-marketing': {
      primary: 'exa',
      fallback: null,
      reason: 'Exa for content research and trending topics'
    }
  };

  return mcpMap[skill] || { primary: null, fallback: null, reason: 'No specific MCP required' };
}

/**
 * Route user request to appropriate skill
 * @param {string} userInput - User's message
 * @param {Object} context - Optional context (conversation history, etc.)
 * @returns {Object} Complete routing decision
 */
function routeRequest(userInput, context = {}) {
  const keywordResult = detectKeywords(userInput);

  if (!keywordResult.skill) {
    return {
      routed: false,
      ...keywordResult
    };
  }

  const mcpHint = getMCPRecommendation(keywordResult.skill);

  return {
    routed: true,
    skill: keywordResult.skill,
    mcp: {
      primary: mcpHint.primary,
      fallback: mcpHint.fallback,
      reason: mcpHint.reason
    },
    confidence: keywordResult.confidence,
    matchedKeyword: keywordResult.keyword,
    alternatives: keywordResult.alternatives,
    reason: keywordResult.reason
  };
}

/**
 * Get all available routes for documentation
 * @returns {Object} All keyword routes grouped by category
 */
function getAvailableRoutes() {
  const categories = {};

  for (const [keyword, route] of Object.entries(KEYWORD_ROUTES)) {
    const skill = route.skill;
    if (!categories[skill]) {
      categories[skill] = [];
    }
    categories[skill].push({
      keyword,
      priority: route.priority,
      mcp: route.mcp
    });
  }

  return categories;
}

// CLI support for testing
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: keyword-router.cjs <user input>');
    console.log('       keyword-router.cjs --list (show all routes)');
    process.exit(0);
  }

  if (args[0] === '--list') {
    console.log(JSON.stringify(getAvailableRoutes(), null, 2));
  } else {
    const input = args.join(' ');
    const result = routeRequest(input);
    console.log(JSON.stringify(result, null, 2));
  }
}

module.exports = {
  detectKeywords,
  getMCPRecommendation,
  routeRequest,
  getAvailableRoutes,
  KEYWORD_ROUTES,
  CONTEXT_MODIFIERS
};
