#!/usr/bin/env node
'use strict';

/**
 * Pre-Tool Router - MCP/Agent selection before tool execution
 *
 * This hook runs before tool execution to:
 * 1. Select optimal MCP server for the operation
 * 2. Route to appropriate agent when needed
 * 3. Apply rate limiting and safety checks
 * 4. Log tool usage for analytics
 *
 * MCP Priority Order:
 * 1. Exa AI - Discovery, research, semantic search
 * 2. Browser-Use - Social platform automation
 * 3. Gmail - Email operations
 * 4. Native tools - File operations, etc.
 *
 * @module pre-tool-router
 */

const fs = require('fs');
const path = require('path');

// MCP Server configurations
const MCP_SERVERS = {
  exa: {
    name: 'Exa AI',
    tools: [
      'linkedin_search_exa',
      'company_research_exa',
      'web_search_exa',
      'deep_researcher_start',
      'deep_researcher_check',
      'exa_search',
      'create_webset',
      'get_webset',
      'list_websets'
    ],
    capabilities: ['discovery', 'research', 'semantic-search', 'websets'],
    healthCheck: null // Will be populated from env
  },
  'browser-use': {
    name: 'Browser-Use MCP',
    tools: [
      'browser_task',
      'list_browser_profiles',
      'monitor_task',
      'list_skills',
      'get_cookies',
      'execute_skill'
    ],
    capabilities: ['linkedin', 'twitter', 'instagram', 'browser-automation'],
    healthCheck: null
  },
  gmail: {
    name: 'Gmail API',
    tools: [
      'gmail_send',
      'gmail_read',
      'gmail_search',
      'gmail_reply'
    ],
    capabilities: ['email', 'inbox', 'compose', 'reply'],
    healthCheck: null
  }
};

// Tool to MCP mapping
const TOOL_MCP_MAP = {
  // Exa tools
  'linkedin_search_exa': 'exa',
  'company_research_exa': 'exa',
  'web_search_exa': 'exa',
  'deep_researcher_start': 'exa',
  'deep_researcher_check': 'exa',
  'exa_search': 'exa',
  'create_webset': 'exa',
  'get_webset': 'exa',
  'list_websets': 'exa',

  // Browser-Use tools
  'browser_task': 'browser-use',
  'list_browser_profiles': 'browser-use',
  'monitor_task': 'browser-use',
  'list_skills': 'browser-use',
  'get_cookies': 'browser-use',
  'execute_skill': 'browser-use',

  // Gmail tools (internal)
  'gmail_send': 'gmail',
  'gmail_read': 'gmail',
  'gmail_search': 'gmail',
  'gmail_reply': 'gmail'
};

// Agent routing configuration
const AGENT_ROUTES = {
  'discovery': {
    agent: 'discovery-engine',
    preferredMCP: 'exa',
    fallbackMCP: 'browser-use',
    description: 'Find people and research companies'
  },
  'linkedin-outreach': {
    agent: 'linkedin-adapter',
    preferredMCP: 'browser-use',
    fallbackMCP: null,
    description: 'LinkedIn automation (connect, message, etc.)'
  },
  'twitter-outreach': {
    agent: 'twitter-adapter',
    preferredMCP: 'browser-use',
    fallbackMCP: null,
    description: 'Twitter automation (follow, DM, etc.)'
  },
  'instagram-outreach': {
    agent: 'instagram-adapter',
    preferredMCP: 'browser-use',
    fallbackMCP: null,
    description: 'Instagram automation (follow, DM, etc.)'
  },
  'email-campaign': {
    agent: 'outreach-manager',
    preferredMCP: 'gmail',
    fallbackMCP: null,
    description: 'Bulk email campaigns'
  },
  'email-single': {
    agent: 'email-composer',
    preferredMCP: 'gmail',
    fallbackMCP: null,
    description: 'Single email composition'
  },
  'content-research': {
    agent: 'content-marketing',
    preferredMCP: 'exa',
    fallbackMCP: null,
    description: 'Content research and planning'
  },
  'seo-analysis': {
    agent: 'seo-optimization',
    preferredMCP: 'exa',
    fallbackMCP: null,
    description: 'SEO keyword research and analysis'
  }
};

// Rate limit tracking (in-memory, resets on restart)
const rateLimits = new Map();

/**
 * Get MCP server for a specific tool
 * @param {string} toolName - Name of the tool
 * @returns {string|null} MCP server name or null
 */
function getMCPForTool(toolName) {
  return TOOL_MCP_MAP[toolName] || null;
}

/**
 * Get all tools for a specific MCP server
 * @param {string} mcpName - MCP server name
 * @returns {string[]} Array of tool names
 */
function getToolsForMCP(mcpName) {
  const server = MCP_SERVERS[mcpName];
  return server ? server.tools : [];
}

/**
 * Select optimal MCP for an operation type
 * @param {string} operationType - Type of operation
 * @returns {Object} Selected MCP configuration
 */
function selectMCPForOperation(operationType) {
  const operationMCPMap = {
    // Discovery operations
    'find-people': { primary: 'exa', secondary: 'browser-use' },
    'research': { primary: 'exa', secondary: null },
    'semantic-search': { primary: 'exa', secondary: null },
    'webset-create': { primary: 'exa', secondary: null },

    // Social operations
    'linkedin-action': { primary: 'browser-use', secondary: null },
    'twitter-action': { primary: 'browser-use', secondary: null },
    'instagram-action': { primary: 'browser-use', secondary: null },
    'browser-task': { primary: 'browser-use', secondary: null },

    // Email operations
    'send-email': { primary: 'gmail', secondary: null },
    'read-inbox': { primary: 'gmail', secondary: null },
    'email-reply': { primary: 'gmail', secondary: null }
  };

  const mapping = operationMCPMap[operationType];
  if (!mapping) {
    return { primary: null, secondary: null, reason: 'Unknown operation type' };
  }

  return {
    primary: mapping.primary,
    secondary: mapping.secondary,
    server: MCP_SERVERS[mapping.primary],
    reason: `Best MCP for ${operationType}`
  };
}

/**
 * Route to appropriate agent based on task context
 * @param {Object} context - Task context
 * @returns {Object} Agent routing decision
 */
function routeToAgent(context) {
  const { taskType, platform, action } = context;

  // Match against agent routes
  for (const [routeKey, route] of Object.entries(AGENT_ROUTES)) {
    if (routeKey === taskType) {
      return {
        agent: route.agent,
        mcp: route.preferredMCP,
        fallback: route.fallbackMCP,
        reason: route.description
      };
    }
  }

  // Platform-specific routing
  if (platform) {
    const platformRoutes = {
      'linkedin': 'linkedin-outreach',
      'twitter': 'twitter-outreach',
      'instagram': 'instagram-outreach',
      'email': action === 'campaign' ? 'email-campaign' : 'email-single'
    };

    const routeKey = platformRoutes[platform];
    if (routeKey && AGENT_ROUTES[routeKey]) {
      const route = AGENT_ROUTES[routeKey];
      return {
        agent: route.agent,
        mcp: route.preferredMCP,
        fallback: route.fallbackMCP,
        reason: route.description
      };
    }
  }

  return {
    agent: null,
    mcp: null,
    fallback: null,
    reason: 'No specific agent route matched'
  };
}

/**
 * Check rate limits for a platform/action
 * @param {string} platform - Platform name
 * @param {string} action - Action type
 * @returns {Object} Rate limit status
 */
function checkRateLimit(platform, action) {
  const key = `${platform}:${action}`;
  const now = Date.now();
  const windowMs = 24 * 60 * 60 * 1000; // 24 hours

  // Default limits per platform/action
  const limits = {
    'linkedin:connect': 30,
    'linkedin:message': 50,
    'linkedin:view': 100,
    'twitter:follow': 50,
    'twitter:dm': 30,
    'twitter:like': 100,
    'instagram:follow': 40,
    'instagram:dm': 20,
    'instagram:like': 100,
    'email:send': 100
  };

  const limit = limits[key] || 50;
  const current = rateLimits.get(key) || { count: 0, windowStart: now };

  // Reset if window expired
  if (now - current.windowStart > windowMs) {
    current.count = 0;
    current.windowStart = now;
  }

  const remaining = limit - current.count;
  const allowed = remaining > 0;

  return {
    allowed,
    limit,
    remaining,
    resetIn: windowMs - (now - current.windowStart),
    key
  };
}

/**
 * Record a rate-limited action
 * @param {string} platform - Platform name
 * @param {string} action - Action type
 */
function recordAction(platform, action) {
  const key = `${platform}:${action}`;
  const now = Date.now();
  const windowMs = 24 * 60 * 60 * 1000;

  const current = rateLimits.get(key) || { count: 0, windowStart: now };

  // Reset if window expired
  if (now - current.windowStart > windowMs) {
    current.count = 1;
    current.windowStart = now;
  } else {
    current.count += 1;
  }

  rateLimits.set(key, current);
}

/**
 * Pre-process a tool call before execution
 * @param {Object} toolCall - Tool call object
 * @returns {Object} Pre-processing result with routing decisions
 */
function preProcessToolCall(toolCall) {
  const { tool, parameters } = toolCall;

  // Get MCP for this tool
  const mcp = getMCPForTool(tool);

  // Extract platform/action for rate limiting
  let platform = null;
  let action = null;

  if (tool.includes('linkedin')) {
    platform = 'linkedin';
    action = parameters?.action || 'unknown';
  } else if (tool.includes('twitter')) {
    platform = 'twitter';
    action = parameters?.action || 'unknown';
  } else if (tool.includes('instagram')) {
    platform = 'instagram';
    action = parameters?.action || 'unknown';
  } else if (tool.includes('gmail') || tool.includes('email')) {
    platform = 'email';
    action = parameters?.action || 'send';
  }

  // Check rate limits
  let rateLimit = { allowed: true };
  if (platform && action) {
    rateLimit = checkRateLimit(platform, action);
  }

  return {
    tool,
    mcp,
    mcpServer: mcp ? MCP_SERVERS[mcp] : null,
    platform,
    action,
    rateLimit,
    allowed: rateLimit.allowed,
    reason: rateLimit.allowed ? 'OK' : `Rate limit exceeded for ${platform}:${action}`
  };
}

/**
 * Log tool usage for analytics
 * @param {Object} toolCall - Tool call details
 * @param {Object} result - Execution result
 */
function logToolUsage(toolCall, result) {
  const logDir = path.join(process.cwd(), 'output', 'logs', 'tool-usage');

  try {
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const logFile = path.join(logDir, `${new Date().toISOString().split('T')[0]}.jsonl`);
    const entry = {
      timestamp: new Date().toISOString(),
      tool: toolCall.tool,
      mcp: toolCall.mcp,
      platform: toolCall.platform,
      action: toolCall.action,
      success: result?.success ?? true,
      duration: result?.duration
    };

    fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
  } catch (err) {
    // Silent fail - logging is non-critical
  }
}

// CLI support for testing
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args[0] === '--help') {
    console.log(`
Pre-Tool Router - MCP/Agent selection utility

Commands:
  --mcp <tool>          Get MCP server for a tool
  --tools <mcp>         List tools for an MCP server
  --route <type>        Get agent route for operation type
  --limit <plat> <act>  Check rate limit
  --servers             List all MCP servers
`);
    process.exit(0);
  }

  if (args[0] === '--mcp' && args[1]) {
    const mcp = getMCPForTool(args[1]);
    console.log(JSON.stringify({ tool: args[1], mcp }, null, 2));
  } else if (args[0] === '--tools' && args[1]) {
    const tools = getToolsForMCP(args[1]);
    console.log(JSON.stringify({ mcp: args[1], tools }, null, 2));
  } else if (args[0] === '--route' && args[1]) {
    const route = routeToAgent({ taskType: args[1] });
    console.log(JSON.stringify(route, null, 2));
  } else if (args[0] === '--limit' && args[1] && args[2]) {
    const limit = checkRateLimit(args[1], args[2]);
    console.log(JSON.stringify(limit, null, 2));
  } else if (args[0] === '--servers') {
    console.log(JSON.stringify(MCP_SERVERS, null, 2));
  }
}

module.exports = {
  MCP_SERVERS,
  TOOL_MCP_MAP,
  AGENT_ROUTES,
  getMCPForTool,
  getToolsForMCP,
  selectMCPForOperation,
  routeToAgent,
  checkRateLimit,
  recordAction,
  preProcessToolCall,
  logToolUsage
};
