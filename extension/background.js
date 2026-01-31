const SERVER_URL = 'http://localhost:3456';
const POLL_INTERVAL = 500;
let connected = false;

function setBadge(status) {
  const config = {
    connected: { text: 'ON', color: '#22c55e' },
    disconnected: { text: 'OFF', color: '#ef4444' },
    busy: { text: '...', color: '#f59e0b' }
  };
  const c = config[status] || config.disconnected;
  chrome.action.setBadgeText({ text: c.text });
  chrome.action.setBadgeBackgroundColor({ color: c.color });
}
setBadge('disconnected');

// ── Inject content script into a tab and verify it's alive ──
async function injectAndVerify(tabId, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      // Inject content.js (handles duplicate injection internally)
      await chrome.scripting.executeScript({ target: { tabId }, files: ['content.js'] });
      await new Promise(r => setTimeout(r, 300));

      // Verify listener is alive by sending a ping
      const result = await chrome.tabs.sendMessage(tabId, { type: '10X_COMMAND', command: 'ping', args: {} });
      if (result && result.success) return { ok: true, tabId };
    } catch (e) {
      if (i < retries - 1) await new Promise(r => setTimeout(r, 500));
    }
  }
  return { ok: false, error: 'Content script injection failed after ' + retries + ' attempts. Refresh the LinkedIn tab (F5).' };
}

// ── Find a LinkedIn tab, inject content script, return ready tab ──
async function getReadyTab() {
  const tabs = await chrome.tabs.query({ url: '*://*.linkedin.com/*' });
  if (!tabs.length) return { ok: false, error: 'No LinkedIn tab open. Please open linkedin.com in Chrome and log in.' };

  // Prefer a fully loaded tab
  const tab = tabs.find(t => t.status === 'complete') || tabs[0];

  // Wait for tab to finish loading if needed
  if (tab.status !== 'complete') {
    await new Promise((resolve) => {
      const listener = (tabId, info) => {
        if (tabId === tab.id && info.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          resolve();
        }
      };
      chrome.tabs.onUpdated.addListener(listener);
      setTimeout(() => { chrome.tabs.onUpdated.removeListener(listener); resolve(); }, 10000);
    });
  }

  return await injectAndVerify(tab.id);
}

// ── Navigate tab to URL and re-inject content script ──
async function navigateAndInject(tabId, url) {
  await chrome.tabs.update(tabId, { url });
  // Wait for page to fully load
  await new Promise((resolve) => {
    const listener = (tid, info) => {
      if (tid === tabId && info.status === 'complete') {
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    };
    chrome.tabs.onUpdated.addListener(listener);
    setTimeout(() => { chrome.tabs.onUpdated.removeListener(listener); resolve(); }, 30000);
  });
  // Extra wait for LinkedIn's SPA to finish rendering
  await new Promise(r => setTimeout(r, 2000));
  // Re-inject content script (old one died with navigation)
  return await injectAndVerify(tabId);
}

// ── Execute a command from the server ──
async function executeCommand(data) {
  try {
    const ready = await getReadyTab();
    if (!ready.ok) {
      await postResult(data.id, { success: false, error: ready.error });
      setBadge('connected');
      return;
    }
    const tabId = ready.tabId;

    // For commands that need multi-page navigation (searchProfiles),
    // handle navigation from background script instead of content script
    if (data.command === 'searchProfiles') {
      const result = await handleSearchProfiles(tabId, data.args || {});
      await postResult(data.id, result);
      if (result && result.success) await updateDailyCounts(data.command);
      setBadge('connected');
      return;
    }

    // For commands that navigate to a profile URL, do navigation from here
    const args = data.args || {};
    if (args.profileUrl) {
      const currentUrl = (await chrome.tabs.get(tabId)).url || '';
      const targetPath = args.profileUrl.replace('https://www.linkedin.com', '');
      if (!currentUrl.includes(targetPath)) {
        const nav = await navigateAndInject(tabId, args.profileUrl);
        if (!nav.ok) {
          await postResult(data.id, { success: false, error: nav.error });
          setBadge('connected');
          return;
        }
      }
      // Tell content script NOT to navigate (we already did it)
      args._skipNavigation = true;
    }

    // Send command to content script
    let result = null;
    try {
      result = await chrome.tabs.sendMessage(tabId, { type: '10X_COMMAND', command: data.command, args, id: data.id });
    } catch (e) {
      // One more inject+retry
      const retry = await injectAndVerify(tabId);
      if (retry.ok) {
        try {
          result = await chrome.tabs.sendMessage(tabId, { type: '10X_COMMAND', command: data.command, args, id: data.id });
        } catch (e2) {
          result = { success: false, error: 'Content script failed: ' + e2.message };
        }
      } else {
        result = { success: false, error: retry.error };
      }
    }

    await postResult(data.id, result);
    if (result && result.success) await updateDailyCounts(data.command);
  } catch (e) {
    await postResult(data.id, { success: false, error: e.message });
  }
  setBadge('connected');
}

// ── Search Profiles: multi-page navigation handled by background ──
async function handleSearchProfiles(tabId, args) {
  const { filters = {}, maxPages = 10 } = args;
  const params = new URLSearchParams();
  if (filters.keywords) params.set('keywords', filters.keywords);
  if (filters.industry) params.set('industry', filters.industry);
  if (filters.location) params.set('geoUrn', filters.location);
  if (filters.company) params.set('company', filters.company);
  if (filters.title) params.set('title', filters.title);
  const baseUrl = 'https://www.linkedin.com/search/results/people/?' + params;

  const allProfiles = [];

  for (let page = 1; page <= maxPages; page++) {
    const url = page === 1 ? baseUrl : baseUrl + '&page=' + page;
    console.log('[10X] Navigating to search page ' + page + '...');

    const nav = await navigateAndInject(tabId, url);
    if (!nav.ok) {
      if (allProfiles.length > 0) return { success: true, profiles: allProfiles, count: allProfiles.length, stoppedAt: page, reason: 'injection_failed' };
      return { success: false, error: nav.error };
    }

    // Ask content script to scrape the current page (no navigation needed)
    let result;
    try {
      result = await chrome.tabs.sendMessage(tabId, { type: '10X_COMMAND', command: 'scrapeCurrentPage', args: {} });
    } catch (e) {
      if (allProfiles.length > 0) return { success: true, profiles: allProfiles, count: allProfiles.length, stoppedAt: page, reason: e.message };
      return { success: false, error: 'Scrape failed on page ' + page + ': ' + e.message };
    }

    if (!result.success) {
      if (result.error === 'CAPTCHA') return { success: false, error: 'CAPTCHA detected. Solve it manually and try again.', profiles: allProfiles };
      if (allProfiles.length > 0) return { success: true, profiles: allProfiles, count: allProfiles.length, stoppedAt: page, reason: result.error };
      return result;
    }

    if (result.profiles) allProfiles.push(...result.profiles);
    if (!result.hasNextPage) break;

    // Short delay between pages
    await new Promise(r => setTimeout(r, 3000));
  }

  return { success: true, profiles: allProfiles, count: allProfiles.length };
}

// ── Post result back to Node.js server ──
async function postResult(id, result) {
  try {
    await fetch(SERVER_URL + '/result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, result }),
      signal: AbortSignal.timeout(5000)
    });
  } catch (e) { console.error('[10X] Post failed:', e); }
}

// ── Daily counts tracking ──
async function updateDailyCounts(command) {
  const today = new Date().toISOString().split('T')[0];
  const data = await chrome.storage.local.get('dailyCounts');
  let counts = data.dailyCounts || {};
  if (counts.date !== today) counts = { date: today, connections: 0, messages: 0, inmails: 0, scrapes: 0 };
  const map = { sendConnection: 'connections', sendMessage: 'messages', sendInMail: 'inmails', searchProfiles: 'scrapes', deepScan: 'scrapes' };
  if (map[command]) counts[map[command]]++;
  await chrome.storage.local.set({ dailyCounts: counts });
}

async function getDailyCounts() {
  const today = new Date().toISOString().split('T')[0];
  const data = await chrome.storage.local.get('dailyCounts');
  let counts = data.dailyCounts || {};
  if (counts.date !== today) counts = { date: today, connections: 0, messages: 0, inmails: 0, scrapes: 0 };
  return counts;
}

// ── Popup status handler ──
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === '10X_GET_STATUS') {
    getDailyCounts().then(counts => sendResponse({ connected, counts }));
    return true;
  }
});

// ── Poll the Node.js server ──
async function poll() {
  try {
    const res = await fetch(SERVER_URL + '/poll', { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    if (!connected) { connected = true; setBadge('connected'); console.log('[10X] Connected to server'); }
    const data = await res.json();
    if (data.command) { setBadge('busy'); await executeCommand(data); }
  } catch (e) {
    if (connected) { connected = false; setBadge('disconnected'); console.log('[10X] Disconnected from server'); }
  }
}

setInterval(poll, POLL_INTERVAL);
poll();
