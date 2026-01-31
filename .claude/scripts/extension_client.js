#!/usr/bin/env node
// 10X LinkedIn Outreach - Extension Client
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
      connections_sent: 0,
      inmails_sent: 0,
      messages_sent: 0,
      profiles_scraped: 0,
      monthly_inmails: 0
    };
  }
}

function writeLimits(limits) {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(LIMITS_FILE, JSON.stringify(limits, null, 2));
}

function incrementLimit(action) {
  const limits = readLimits();
  const map = {
    sendConnection: 'connections_sent',
    sendInMail: 'inmails_sent',
    sendMessage: 'messages_sent',
    searchProfiles: 'profiles_scraped',
    deepScan: 'profiles_scraped'
  };
  const key = map[action];
  if (key) {
    limits[key]++;
    if (action === 'sendInMail') limits.monthly_inmails++;
  }
  writeLimits(limits);
  return limits;
}

function checkLimit(action) {
  const limits = readLimits();
  const map = {
    sendConnection: 'connections_sent',
    sendInMail: 'inmails_sent',
    sendMessage: 'messages_sent',
    searchProfiles: 'profiles_scraped',
    deepScan: 'profiles_scraped'
  };
  const key = map[action];
  if (key && limits[key] >= DAILY_LIMITS[key]) {
    return { allowed: false, reason: `Daily limit reached: ${limits[key]}/${DAILY_LIMITS[key]} ${key}` };
  }
  if (action === 'sendInMail' && limits.monthly_inmails >= MONTHLY_INMAIL_LIMIT) {
    return { allowed: false, reason: `Monthly InMail limit reached: ${limits.monthly_inmails}/${MONTHLY_INMAIL_LIMIT}` };
  }
  return { allowed: true };
}

let pendingCommand = null;
let pendingResolve = null;
let commandId = 0;

function startServer() {
  const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    if (req.method === 'GET' && req.url === '/poll') {
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

    if (req.method === 'POST' && req.url === '/result') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          if (pendingResolve) {
            pendingResolve(data.result);
            pendingResolve = null;
          }
        } catch {}
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
      });
      return;
    }

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
      res.end(JSON.stringify({ server: 'running', limits: readLimits() }));
      return;
    }

    res.writeHead(404);
    res.end('Not found');
  });

  server.listen(PORT, () => {
    console.log(`[10X] Server running on http://localhost:${PORT}`);
  });

  return server;
}

function sendCommand(command, args) {
  return new Promise((resolve, reject) => {
    const id = ++commandId;
    const limitCheck = checkLimit(command);
    if (!limitCheck.allowed) {
      resolve({ success: false, error: 'RATE_LIMITED', message: limitCheck.reason });
      return;
    }
    pendingCommand = { id, command, args };
    pendingResolve = (result) => {
      if (result && result.success) {
        incrementLimit(command);
      }
      resolve(result);
    };
    setTimeout(() => {
      if (pendingResolve) {
        pendingResolve = null;
        pendingCommand = null;
        resolve({ success: false, error: 'TIMEOUT', message: 'Extension did not respond within 60s' });
      }
    }, 60000);
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (args[0] === '--server') {
    startServer();
    return;
  }
  if (args.length === 0) {
    console.log(`Usage:
  node extension_client.js --server              Start HTTP server
  node extension_client.js ping                   Test extension connection
  node extension_client.js searchProfiles '{...}' Search LinkedIn profiles
  node extension_client.js sendConnection '{...}' Send connection request
  node extension_client.js sendInMail '{...}'     Send InMail
  node extension_client.js checkAcceptance '{..}' Check connection status
  node extension_client.js deepScan '{...}'       Deep scan a profile
  node extension_client.js sendMessage '{...}'    Send message
  node extension_client.js getStatus              Get server status
  node extension_client.js getLimits              Get rate limits`);
    process.exit(0);
  }
  const command = args[0];
  if (command === 'getLimits') {
    console.log(JSON.stringify(readLimits(), null, 2));
    process.exit(0);
  }
  const server = startServer();
  if (command === 'getStatus') {
    setTimeout(() => {
      console.log(JSON.stringify({ server: 'running', limits: readLimits() }));
      server.close();
      process.exit(0);
    }, 100);
    return;
  }
  let cmdArgs = {};
  if (args[1]) {
    try {
      cmdArgs = JSON.parse(args[1]);
    } catch {
      console.error('Invalid JSON argument');
      process.exit(1);
    }
  }
  console.error('[10X] Waiting for extension to connect...');
  const result = await sendCommand(command, cmdArgs);
  console.log(JSON.stringify(result, null, 2));
  server.close();
  process.exit(result.success ? 0 : 1);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
