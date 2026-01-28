#!/usr/bin/env node
/**
 * 10x Outreach Skill — Cross-platform port manager
 * Usage: node scripts/port-manager.js <command> [port]
 * Commands: check <port>, free <port>, find <startPort>
 */

import net from 'net';
import { execSync } from 'child_process';

const [,, cmd, portArg] = process.argv;
const port = parseInt(portArg) || 3000;

function checkPort(p) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => { server.close(); resolve(true); });
    server.listen(p, '127.0.0.1');
  });
}

async function findFreePort(start) {
  for (let p = start; p < start + 100; p++) {
    if (await checkPort(p)) return p;
  }
  return null;
}

function freePort(p) {
  const isWin = process.platform === 'win32';
  try {
    if (isWin) {
      const out = execSync(`netstat -ano | findstr :${p}`, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
      const pids = [...new Set(out.split('\n').map(l => l.trim().split(/\s+/).pop()).filter(x => x && x !== '0'))];
      for (const pid of pids) {
        try { execSync(`taskkill /PID ${pid} /F`, { stdio: 'pipe' }); } catch {}
      }
      console.log(`Freed port ${p} (killed PIDs: ${pids.join(', ')})`);
    } else {
      execSync(`lsof -ti :${p} | xargs kill -9 2>/dev/null || true`, { stdio: 'pipe' });
      console.log(`Freed port ${p}`);
    }
  } catch {
    console.log(`Port ${p} is already free`);
  }
}

switch (cmd) {
  case 'check':
    checkPort(port).then(free => {
      console.log(free ? `Port ${port} is available` : `Port ${port} is in use`);
      process.exit(free ? 0 : 1);
    });
    break;
  case 'free':
    freePort(port);
    break;
  case 'find':
    findFreePort(port).then(p => {
      if (p) console.log(p);
      else { console.error('No free port found'); process.exit(1); }
    });
    break;
  default:
    console.log('Usage: node scripts/port-manager.js <check|free|find> [port]');
    process.exit(1);
}
