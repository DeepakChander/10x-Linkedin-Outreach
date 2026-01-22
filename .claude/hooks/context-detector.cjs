#!/usr/bin/env node
'use strict';

/**
 * Context Detector - User intent analysis and context extraction
 *
 * Analyzes user messages to:
 * 1. Detect intent (what the user wants to do)
 * 2. Extract entities (people, companies, platforms)
 * 3. Identify context (campaign, single action, research)
 * 4. Determine urgency and priority
 *
 * This information helps route requests to appropriate skills/MCPs.
 *
 * @module context-detector
 */

const fs = require('fs');
const path = require('path');

// Intent patterns with confidence scores
const INTENT_PATTERNS = {
  // Discovery intents
  'discover-people': {
    patterns: [
      /find\s+(?:people|contacts?|leads?|prospects?)/i,
      /discover\s+(?:people|contacts?|leads?|prospects?)/i,
      /search\s+for\s+(?:people|contacts?|founders?|executives?)/i,
      /looking\s+for\s+(?:people|contacts?)/i,
      /who\s+(?:are|is)\s+(?:the|at)/i
    ],
    confidence: 0.9,
    skill: 'discovery-engine',
    mcp: 'exa'
  },
  'research-company': {
    patterns: [
      /research\s+(?:company|companies|startup|startups|business)/i,
      /find\s+(?:out|info|information)\s+about/i,
      /what\s+(?:is|does)\s+\w+\s+(?:company|do|work)/i,
      /company\s+(?:info|information|details|research)/i
    ],
    confidence: 0.85,
    skill: 'discovery-engine',
    mcp: 'exa'
  },

  // Email intents
  'send-campaign': {
    patterns: [
      /send\s+(?:email\s+)?campaign/i,
      /bulk\s+email/i,
      /cold\s+(?:email|outreach)/i,
      /email\s+(?:the\s+)?(?:list|contacts?|leads?)/i,
      /outreach\s+to\s+\d+/i,
      /mass\s+email/i
    ],
    confidence: 0.95,
    skill: 'outreach-manager',
    mcp: 'gmail'
  },
  'compose-email': {
    patterns: [
      /(?:write|compose|draft)\s+(?:an?\s+)?email/i,
      /send\s+(?:an?\s+)?email\s+to\s+\w+/i,
      /email\s+(?:him|her|them|this\s+person)/i
    ],
    confidence: 0.9,
    skill: 'email-composer',
    mcp: 'gmail'
  },
  'check-inbox': {
    patterns: [
      /check\s+(?:my\s+)?(?:inbox|email)/i,
      /(?:read|show|get)\s+(?:my\s+)?emails?/i,
      /what(?:'s|\s+is)\s+in\s+my\s+inbox/i,
      /any\s+(?:new\s+)?emails?/i,
      /unread\s+emails?/i
    ],
    confidence: 0.9,
    skill: 'inbox-reader',
    mcp: 'gmail'
  },
  'reply-email': {
    patterns: [
      /reply\s+to\s+(?:this|the|that)\s+email/i,
      /respond\s+to\s+(?:this|the|that)/i,
      /write\s+(?:a\s+)?reply/i,
      /answer\s+(?:this|the)\s+email/i
    ],
    confidence: 0.9,
    skill: 'reply-generator',
    mcp: 'gmail'
  },
  'summarize-email': {
    patterns: [
      /summarize\s+(?:my\s+)?(?:inbox|emails?)/i,
      /email\s+(?:summary|digest)/i,
      /what(?:'s|\s+is)\s+important\s+in/i,
      /(?:daily|weekly)\s+digest/i
    ],
    confidence: 0.85,
    skill: 'email-summarizer',
    mcp: 'gmail'
  },

  // Social platform intents
  'linkedin-action': {
    patterns: [
      /connect\s+(?:with|on)\s+linkedin/i,
      /linkedin\s+(?:connect|message|dm|view|like)/i,
      /send\s+(?:a\s+)?connection\s+request/i,
      /(?:message|dm)\s+(?:on|via)\s+linkedin/i
    ],
    confidence: 0.9,
    skill: 'linkedin-adapter',
    mcp: 'browser-use'
  },
  'twitter-action': {
    patterns: [
      /(?:follow|dm|message|tweet)\s+(?:on|via)\s+twitter/i,
      /twitter\s+(?:follow|dm|like|retweet)/i,
      /send\s+(?:a\s+)?dm\s+(?:on\s+)?(?:twitter|x)/i
    ],
    confidence: 0.9,
    skill: 'twitter-adapter',
    mcp: 'browser-use'
  },
  'instagram-action': {
    patterns: [
      /(?:follow|dm|message)\s+(?:on|via)\s+instagram/i,
      /instagram\s+(?:follow|dm|like|comment)/i,
      /(?:ig|insta)\s+(?:dm|follow)/i
    ],
    confidence: 0.9,
    skill: 'instagram-adapter',
    mcp: 'browser-use'
  },

  // Workflow intents
  'create-workflow': {
    patterns: [
      /create\s+(?:a\s+)?workflow/i,
      /design\s+(?:a\s+)?(?:workflow|campaign|sequence)/i,
      /set\s+up\s+(?:a\s+)?(?:workflow|automation)/i,
      /multi[-\s]?(?:step|platform)\s+(?:campaign|outreach)/i
    ],
    confidence: 0.9,
    skill: 'workflow-engine',
    mcp: null
  },
  'run-workflow': {
    patterns: [
      /run\s+(?:the\s+)?workflow/i,
      /execute\s+(?:the\s+)?workflow/i,
      /start\s+(?:the\s+)?campaign/i,
      /launch\s+(?:the\s+)?workflow/i
    ],
    confidence: 0.9,
    skill: 'workflow-engine',
    mcp: null
  },

  // Content & SEO intents
  'content-create': {
    patterns: [
      /(?:write|create|draft)\s+(?:a\s+)?(?:blog|article|post)/i,
      /content\s+(?:for|about|on)/i,
      /(?:social\s+)?media\s+(?:post|content)/i,
      /content\s+calendar/i
    ],
    confidence: 0.85,
    skill: 'content-marketing',
    mcp: 'exa'
  },
  'seo-analysis': {
    patterns: [
      /(?:seo|keyword)\s+(?:research|analysis)/i,
      /optimize\s+(?:for|content)/i,
      /(?:find|research)\s+keywords/i,
      /backlink\s+(?:analysis|research)/i,
      /ranking\s+(?:check|analysis)/i
    ],
    confidence: 0.9,
    skill: 'seo-optimization',
    mcp: 'exa'
  },

  // Analytics intents
  'view-analytics': {
    patterns: [
      /(?:show|view|get)\s+(?:my\s+)?(?:analytics|metrics|stats)/i,
      /(?:campaign|outreach)\s+(?:performance|results)/i,
      /how\s+(?:is|are|did)\s+(?:my|the)\s+(?:campaign|outreach)/i,
      /(?:email|campaign)\s+(?:stats|statistics)/i
    ],
    confidence: 0.85,
    skill: 'analytics',
    mcp: null
  },

  // Team management intents
  'manage-team': {
    patterns: [
      /(?:add|remove|manage)\s+team/i,
      /team\s+(?:member|credentials?|setup)/i,
      /(?:configure|setup)\s+(?:team|user)/i
    ],
    confidence: 0.85,
    skill: 'team-manager',
    mcp: null
  },

  // Template intents
  'manage-template': {
    patterns: [
      /(?:create|edit|manage)\s+template/i,
      /(?:email|message)\s+template/i,
      /template\s+(?:for|to)/i
    ],
    confidence: 0.8,
    skill: 'template-manager',
    mcp: null
  }
};

// Entity extraction patterns
const ENTITY_PATTERNS = {
  email: /[\w.-]+@[\w.-]+\.\w+/gi,
  url: /https?:\/\/[^\s]+/gi,
  linkedinUrl: /(?:linkedin\.com\/in\/|linkedin\.com\/company\/)[^\s]+/gi,
  twitterHandle: /@[\w_]+/g,
  phone: /\+?[\d\s()-]{10,}/g,
  company: /(?:at|@|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/g,
  number: /\b\d+\b/g,
  personName: /(?:to|for|reach|contact)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/g
};

// Context indicators
const CONTEXT_INDICATORS = {
  bulk: ['bulk', 'multiple', 'batch', 'list', 'all', 'campaign', 'mass'],
  single: ['one', 'single', 'individual', 'this', 'that', 'specific'],
  urgent: ['urgent', 'asap', 'now', 'immediately', 'quick', 'fast'],
  scheduled: ['schedule', 'later', 'tomorrow', 'next week', 'at', 'on'],
  research: ['research', 'find out', 'learn', 'discover', 'analyze']
};

/**
 * Detect user intent from message
 * @param {string} message - User message
 * @returns {Object} Detected intent with confidence
 */
function detectIntent(message) {
  const results = [];

  for (const [intentName, config] of Object.entries(INTENT_PATTERNS)) {
    for (const pattern of config.patterns) {
      if (pattern.test(message)) {
        results.push({
          intent: intentName,
          confidence: config.confidence,
          skill: config.skill,
          mcp: config.mcp,
          pattern: pattern.source
        });
        break; // Only count each intent once
      }
    }
  }

  // Sort by confidence
  results.sort((a, b) => b.confidence - a.confidence);

  if (results.length === 0) {
    return {
      intent: 'unknown',
      confidence: 0,
      skill: null,
      mcp: null,
      alternatives: []
    };
  }

  const best = results[0];
  return {
    intent: best.intent,
    confidence: best.confidence,
    skill: best.skill,
    mcp: best.mcp,
    alternatives: results.slice(1, 3).map(r => ({
      intent: r.intent,
      confidence: r.confidence
    }))
  };
}

/**
 * Extract entities from message
 * @param {string} message - User message
 * @returns {Object} Extracted entities
 */
function extractEntities(message) {
  const entities = {};

  for (const [entityType, pattern] of Object.entries(ENTITY_PATTERNS)) {
    const matches = message.match(pattern);
    if (matches && matches.length > 0) {
      entities[entityType] = [...new Set(matches)]; // Deduplicate
    }
  }

  return entities;
}

/**
 * Detect context from message
 * @param {string} message - User message
 * @returns {Object} Context indicators
 */
function detectContext(message) {
  const lower = message.toLowerCase();
  const context = {
    isBulk: false,
    isSingle: false,
    isUrgent: false,
    isScheduled: false,
    isResearch: false
  };

  for (const indicator of CONTEXT_INDICATORS.bulk) {
    if (lower.includes(indicator)) {
      context.isBulk = true;
      break;
    }
  }

  for (const indicator of CONTEXT_INDICATORS.single) {
    if (lower.includes(indicator)) {
      context.isSingle = true;
      break;
    }
  }

  for (const indicator of CONTEXT_INDICATORS.urgent) {
    if (lower.includes(indicator)) {
      context.isUrgent = true;
      break;
    }
  }

  for (const indicator of CONTEXT_INDICATORS.scheduled) {
    if (lower.includes(indicator)) {
      context.isScheduled = true;
      break;
    }
  }

  for (const indicator of CONTEXT_INDICATORS.research) {
    if (lower.includes(indicator)) {
      context.isResearch = true;
      break;
    }
  }

  // Determine priority
  if (context.isUrgent) {
    context.priority = 'high';
  } else if (context.isScheduled) {
    context.priority = 'low';
  } else {
    context.priority = 'normal';
  }

  return context;
}

/**
 * Analyze user message completely
 * @param {string} message - User message
 * @returns {Object} Complete analysis
 */
function analyzeMessage(message) {
  const intent = detectIntent(message);
  const entities = extractEntities(message);
  const context = detectContext(message);

  // Adjust skill based on context
  let recommendedSkill = intent.skill;
  if (intent.skill === 'email-composer' && context.isBulk) {
    recommendedSkill = 'outreach-manager';
  }
  if (intent.skill === 'outreach-manager' && context.isSingle) {
    recommendedSkill = 'email-composer';
  }

  return {
    intent: intent.intent,
    confidence: intent.confidence,
    skill: recommendedSkill,
    originalSkill: intent.skill,
    mcp: intent.mcp,
    entities,
    context,
    alternatives: intent.alternatives
  };
}

/**
 * Get skill recommendation with reasoning
 * @param {string} message - User message
 * @returns {Object} Skill recommendation with explanation
 */
function getRecommendation(message) {
  const analysis = analyzeMessage(message);

  if (!analysis.skill) {
    return {
      skill: null,
      reason: 'Could not determine user intent',
      suggestions: [
        'Try being more specific about what you want to do',
        'Use keywords like "send email", "find people", "linkedin connect"',
        'Specify a platform or action'
      ]
    };
  }

  const reasons = [];
  reasons.push(`Detected intent: ${analysis.intent}`);

  if (Object.keys(analysis.entities).length > 0) {
    reasons.push(`Found entities: ${Object.keys(analysis.entities).join(', ')}`);
  }

  if (analysis.context.isBulk) {
    reasons.push('Context suggests bulk operation');
  }
  if (analysis.context.isUrgent) {
    reasons.push('Marked as urgent');
  }

  return {
    skill: analysis.skill,
    mcp: analysis.mcp,
    confidence: analysis.confidence,
    reason: reasons.join('. '),
    analysis
  };
}

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: context-detector.cjs "<user message>"');
    console.log('       context-detector.cjs --intents (list all intents)');
    process.exit(0);
  }

  if (args[0] === '--intents') {
    const intents = Object.keys(INTENT_PATTERNS).map(name => ({
      name,
      skill: INTENT_PATTERNS[name].skill,
      mcp: INTENT_PATTERNS[name].mcp
    }));
    console.log(JSON.stringify(intents, null, 2));
  } else {
    const message = args.join(' ');
    const result = getRecommendation(message);
    console.log(JSON.stringify(result, null, 2));
  }
}

module.exports = {
  detectIntent,
  extractEntities,
  detectContext,
  analyzeMessage,
  getRecommendation,
  INTENT_PATTERNS,
  ENTITY_PATTERNS,
  CONTEXT_INDICATORS
};
