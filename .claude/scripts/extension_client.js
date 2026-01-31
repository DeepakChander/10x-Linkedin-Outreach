#!/usr/bin/env node
// 10X LinkedIn Outreach - Extension Client
// Auto-starts server, waits for extension handshake, then sends command.
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3456;
const OUTPUT_DIR = path.join(__dirname, '..', '..', 'output');
const LIMITS_FILE = path.join(OUTPUT_DIR, '.limits.json');

const DAILY_LIMITS = {
  connections_sent: 20,
  inmails_sent: 10,
  messages_sent: 40,
  profiles_scraped: 100
};
const MONTHLY_INMAIL_LIMIT = 50;

// ── Rate Limits ──────────────────────────────────────────────
function readLimits() {
  try {
    const data = JSON.parse(fs.readFileSync(LIMITS_FILE, 'utf8'));
    const today = new Date().toISOString().split('T')[0];
    if (data.date !== today) {
      data.date = today;
      data.connections_sent = 0;
      data.inmails_sent = 0;
      data.messages_sent = 0;
      data.profiles_scraped = 0;
      if (new Date().getDate() === 1) data.monthly_inmails = 0;
    }
    return data;
  } catch {
    return {
      date: new Date().toISOString().split('T')[0],
      connections_sent: 0, inmails_sent: 0,
      messages_sent: 0, profiles_scraped: 0, monthly_inmails: 0
    };
  }
}

function writeLimits(limits) {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(LIMITS_FILE, JSON.stringify(limits, null, 2));
}

function incrementLimit(action) {
  const limits = readLimits();
  const map = { sendConnection: 'connections_sent', sendInMail: 'inmails_sent', sendMessage: 'messages_sent', searchProfiles: 'profiles_scraped', deepScan: 'profiles_scraped' };
  const key = map[action];
  if (key) { limits[key]++; if (action === 'sendInMail') limits.monthly_inmails++; }
  writeLimits(limits);
  return limits;
}

function checkLimit(action) {
  const limits = readLimits();
  const map = { sendConnection: 'connections_sent', sendInMail: 'inmails_sent', sendMessage: 'messages_sent', searchProfiles: 'profiles_scraped', deepScan: 'profiles_scraped' };
  const key = map[action];
  if (key && limits[key] >= DAILY_LIMITS[key]) return { allowed: false, reason: `Daily limit reached: ${limits[key]}/${DAILY_LIMITS[key]} ${key}` };
  if (action === 'sendInMail' && limits.monthly_inmails >= MONTHLY_INMAIL_LIMIT) return { allowed: false, reason: `Monthly InMail limit: ${limits.monthly_inmails}/${MONTHLY_INMAIL_LIMIT}` };
  return { allowed: true };
}

// ── Server State ─────────────────────────────────────────────
let pendingCommand = null;
let pendingResolve = null;
let commandId = 0;
let extensionConnected = false;
let extensionReadyResolve = null; // resolves when extension first polls

function startServer() {
  return new Promise((resolveStart, rejectStart) => {
    const server = http.createServer((req, res) => {
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

      // Extension polls this endpoint
      if (req.method === 'GET' && req.url === '/poll') {
        // Mark extension as connected on first poll
        if (!extensionConnected) {
          extensionConnected = true;
          if (extensionReadyResolve) { extensionReadyResolve(); extensionReadyResolve = null; }
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        if (pendingCommand) {
          const cmd = pendingCommand;
          pendingCommand = null;
          res.end(JSON.stringify(cmd));
        } else {
          res.end(JSON.stringify({ command: null }));
        }
        return;
      }

      // Extension posts results here
      if (req.method === 'POST' && req.url === '/result') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
          try {
            const data = JSON.parse(body);
            if (pendingResolve) { pendingResolve(data.result); pendingResolve = null; }
          } catch {}
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: true }));
        });
        return;
      }

      // External command API
      if (req.method === 'POST' && req.url === '/command') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
          try {
            const data = JSON.parse(body);
            sendCommand(data.command, data.args || {}).then(result => {
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify(result));
            });
          } catch (e) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
        return;
      }

      if (req.method === 'GET' && req.url === '/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ server: 'running', extensionConnected, limits: readLimits() }));
        return;
      }

      res.writeHead(404); res.end('Not found');
    });

    server.on('error', (e) => {
      if (e.code === 'EADDRINUSE') {
        // Server already running — that's fine, we can send commands via HTTP
        rejectStart(e);
      } else {
        rejectStart(e);
      }
    });

    server.listen(PORT, () => {
      console.error(`[10X] Server started on http://localhost:${PORT}`);
      resolveStart(server);
    });
  });
}

// Wait for extension to make its first /poll request
function waitForExtension(timeoutMs = 30000) {
  if (extensionConnected) return Promise.resolve();
  return new Promise((resolve, reject) => {
    extensionReadyResolve = resolve;
    setTimeout(() => {
      if (!extensionConnected) {
        extensionReadyResolve = null;
        reject(new Error('Extension did not connect within ' + (timeoutMs / 1000) + 's. Make sure:\n  1. Chrome is open\n  2. Extension "10X LinkedIn" is enabled in chrome://extensions\n  3. A linkedin.com tab is open and you are logged in'));
      }
    }, timeoutMs);
  });
}

function sendCommand(command, args) {
  return new Promise((resolve) => {
    const id = ++commandId;
    const limitCheck = checkLimit(command);
    if (!limitCheck.allowed) {
      resolve({ success: false, error: 'RATE_LIMITED', message: limitCheck.reason });
      return;
    }
    pendingCommand = { id, command, args };
    pendingResolve = (result) => {
      if (result && result.success) incrementLimit(command);
      resolve(result);
    };
    // Long timeout for commands like searchProfiles that navigate multiple pages
    const timeout = command === 'searchProfiles' ? 300000 : 120000;
    setTimeout(() => {
      if (pendingResolve) {
        pendingResolve = null;
        pendingCommand = null;
        resolve({ success: false, error: 'TIMEOUT', message: `Extension did not respond within ${timeout / 1000}s` });
      }
    }, timeout);
  });
}

// Send command via HTTP to an already-running server
function sendCommandViaHTTP(command, args) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ command, args });
    const req = http.request({ hostname: '127.0.0.1', port: PORT, path: '/command', method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }, timeout: 300000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch { reject(new Error('Bad response')); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('HTTP timeout')); });
    req.write(body);
    req.end();
  });
}

// ── Main ─────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);

  if (args[0] === '--server') {
    await startServer();
    console.error('[10X] Server running in persistent mode. Press Ctrl+C to stop.');
    return; // keep alive
  }

  if (args.length === 0) {
    console.log(`Usage:
  node extension_client.js --server              Start persistent server
  node extension_client.js ping                   Test connection
  node extension_client.js searchProfiles '{...}' Search LinkedIn
  node extension_client.js sendConnection '{...}' Send connection
  node extension_client.js sendInMail '{...}'     Send InMail
  node extension_client.js checkAcceptance '{..}' Check status
  node extension_client.js deepScan '{...}'       Deep scan profile
  node extension_client.js sendMessage '{...}'    Send message
  node extension_client.js getStatus              Server status
  node extension_client.js getLimits              Rate limits`);
    process.exit(0);
  }

  const command = args[0];
  if (command === 'getLimits') {
    console.log(JSON.stringify(readLimits(), null, 2));
    process.exit(0);
  }

  // Parse args
  let cmdArgs = {};
  if (args[1]) {
    try { cmdArgs = JSON.parse(args[1]); }
    catch { console.error('Invalid JSON argument'); process.exit(1); }
  }

  // Try connecting to existing server first
  let server = null;
  let useHTTP = false;
  try {
    server = await startServer();
  } catch (e) {
    if (e.code === 'EADDRINUSE') {
      console.error('[10X] Server already running on port ' + PORT + ', sending command via HTTP...');
      useHTTP = true;
    } else {
      console.error('[10X] Failed to start server:', e.message);
      process.exit(1);
    }
  }

  if (useHTTP) {
    // Server already running, send via HTTP
    try {
      const result = await sendCommandViaHTTP(command, cmdArgs);
      console.log(JSON.stringify(result, null, 2));
      process.exit(result && result.success ? 0 : 1);
    } catch (e) {
      console.error('[10X] HTTP command failed:', e.message);
      process.exit(1);
    }
    return;
  }

  if (command === 'getStatus') {
    console.log(JSON.stringify({ server: 'running', extensionConnected, limits: readLimits() }));
    server.close(); process.exit(0);
    return;
  }

  // Wait for extension to connect (handshake)
  console.error('[10X] Waiting for Chrome extension to connect...');
  try {
    await waitForExtension(30000);
  } catch (e) {
    console.error('[10X] ' + e.message);
    console.log(JSON.stringify({ success: false, error: 'EXTENSION_NOT_CONNECTED', message: e.message }));
    server.close(); process.exit(1);
    return;
  }
  console.error('[10X] Extension connected! Sending command: ' + command);

  // First send a ping to verify content script is alive
  if (command !== 'ping') {
    const pingResult = await sendCommand('ping', {});
    if (!pingResult || !pingResult.success) {
      console.error('[10X] Content script not ready: ' + JSON.stringify(pingResult));
      console.log(JSON.stringify({ success: false, error: 'CONTENT_SCRIPT_NOT_READY', message: 'Extension connected but content script failed. Refresh LinkedIn tab (F5) and try again.' }));
      server.close(); process.exit(1);
      return;
    }
    console.error('[10X] Content script verified. LinkedIn logged in: ' + (pingResult.loggedIn ? 'Yes' : 'No'));
    if (!pingResult.loggedIn) {
      console.log(JSON.stringify({ success: false, error: 'NOT_LOGGED_IN', message: 'Please log in to LinkedIn in Chrome and try again.' }));
      server.close(); process.exit(1);
      return;
    }
  }

  // Send the actual command
  const result = await sendCommand(command, cmdArgs);
  console.log(JSON.stringify(result, null, 2));
  server.close();
  process.exit(result && result.success ? 0 : 1);
}

main().catch(e => { console.error(e); process.exit(1); });
