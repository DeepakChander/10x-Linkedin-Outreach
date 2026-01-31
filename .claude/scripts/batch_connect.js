#!/usr/bin/env node
// Batch connect: deep scan + send connection for all discovered profiles
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROFILES_FILE = path.join(__dirname, '..', '..', 'output', 'profiles.json');
const NOTE_TEMPLATE = "Hi {{first_name}}, your {{specific_insight}} at {{company}} caught my attention. I'm exploring how leaders like you are approaching AI in practice. Would love to connect.";
const DELAY_MS = 5000;

function run(cmd) {
  try {
    const out = execSync(cmd, { cwd: path.join(__dirname, '..', '..'), timeout: 90000, encoding: 'utf8' });
    const lines = out.trim().split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      try { return JSON.parse(lines[i]); } catch {}
    }
    return { success: false, error: 'No JSON in output' };
  } catch (e) {
    const out = (e.stdout || '') + (e.stderr || '');
    const lines = out.trim().split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      try { return JSON.parse(lines[i]); } catch {}
    }
    return { success: false, error: e.message.substring(0, 200) };
  }
}

function save(profiles) {
  fs.writeFileSync(PROFILES_FILE, JSON.stringify(profiles, null, 2));
}

const profiles = JSON.parse(fs.readFileSync(PROFILES_FILE, 'utf8'));
const discovered = profiles.filter(p => p.status === 'discovered');

if (!discovered.length) {
  console.log('No discovered profiles. Run /discover first.');
  process.exit(0);
}

console.log('Processing ' + discovered.length + ' profiles...\n');

const stats = { sent: 0, already_connected: 0, pending: 0, inmail: 0, failed: 0 };
let stopped = false;

for (let i = 0; i < discovered.length; i++) {
  const p = discovered[i];
  const idx = profiles.findIndex(x => x.id === p.id);
  console.log('--- ' + (i + 1) + '/' + discovered.length + ': ' + p.name + ' (' + p.degree + ') ---');

  // Deep scan
  const scanArg = JSON.stringify({ profileUrl: p.profileUrl });
  const scan = run('node .claude/scripts/extension_client.js deepScan ' + JSON.stringify(scanArg));
  if (scan.success && scan.profile) {
    profiles[idx].deep_scan = scan.profile;
    profiles[idx].headline = scan.profile.headline || p.headline;
    profiles[idx].location = scan.profile.location || p.location;
    console.log('  Scanned: ' + (scan.profile.headline || 'no headline').substring(0, 70));
  } else {
    console.log('  Scan failed: ' + (scan.error || 'unknown'));
  }

  // Build personalized note
  const ds = profiles[idx].deep_scan || {};
  const firstName = (ds.name || p.name || '').split(/\s/)[0];
  const company = ds.company || 'your company';
  const insight = ds.headline ? ds.headline.split('|')[0].trim() : 'work in AI';
  const note = NOTE_TEMPLATE
    .replace('{{first_name}}', firstName)
    .replace('{{specific_insight}}', insight)
    .replace('{{company}}', company);

  // Send connection
  const connArg = JSON.stringify({ profileUrl: p.profileUrl, note: note });
  const result = run('node .claude/scripts/extension_client.js sendConnection ' + JSON.stringify(connArg));

  if (result.success) {
    profiles[idx].status = 'connection_sent';
    profiles[idx].connected_at = new Date().toISOString();
    profiles[idx].connection_note = note;
    stats.sent++;
    console.log('  -> CONNECTION SENT');
  } else if (result.error === 'ALREADY_CONNECTED') {
    profiles[idx].status = 'already_connected';
    stats.already_connected++;
    console.log('  -> Already connected (skipped)');
  } else if (result.error === 'PENDING') {
    profiles[idx].status = 'pending';
    stats.pending++;
    console.log('  -> Pending (skipped)');
  } else if (result.error === 'WEEKLY_LIMIT') {
    save(profiles);
    console.log('  -> WEEKLY LIMIT REACHED - stopping');
    stopped = true;
    break;
  } else if (result.error === 'CAPTCHA') {
    save(profiles);
    console.log('  -> CAPTCHA DETECTED - stopping. Solve it and re-run.');
    stopped = true;
    break;
  } else if (result.error === 'NO_CONNECT_BUTTON' || result.error === 'FOLLOW_ONLY') {
    // No connect button (Follow only or no button) — send InMail instead
    console.log('  -> No connect button, trying InMail...');
    const subj = firstName + ", quick thought on " + company + "'s approach";
    const body = "Hi " + firstName + ", I came across your profile and was impressed by " + insight + ". Would love to connect and share ideas on AI automation.";
    const imArg = JSON.stringify({ profileUrl: p.profileUrl, subject: subj, body: body });
    const imResult = run('node .claude/scripts/extension_client.js sendInMail ' + JSON.stringify(imArg));
    if (imResult.success) {
      profiles[idx].status = 'inmail_sent';
      stats.inmail++;
      console.log('  -> INMAIL SENT');
    } else {
      stats.failed++;
      console.log('  -> InMail failed: ' + (imResult.error || ''));
    }
  } else {
    stats.failed++;
    console.log('  -> Failed: ' + (result.error || result.message || 'unknown'));
  }

  save(profiles);

  // 5 second delay before next
  if (i < discovered.length - 1 && !stopped) {
    const start = Date.now();
    while (Date.now() - start < DELAY_MS) {}
  }
}

console.log('\n=== RESULTS ===');
console.log('Connections sent: ' + stats.sent);
console.log('Already connected: ' + stats.already_connected);
console.log('Pending: ' + stats.pending);
console.log('InMails sent: ' + stats.inmail);
console.log('Failed: ' + stats.failed);
if (stopped) console.log('STOPPED EARLY (weekly limit or CAPTCHA)');
console.log('\nRun /message to follow up with accepted connections.');
