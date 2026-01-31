// Guard against multiple injections — remove old listener
if (window.__10X_LISTENER) { try { chrome.runtime.onMessage.removeListener(window.__10X_LISTENER); } catch {} }
window.__10X_CONTENT_READY = true;

// ── Selectors ──
const S = {
  connectButton: ['button[aria-label*="Invite"][aria-label*="connect"]', 'button.pvs-profile-actions__action[aria-label*="Connect"]', 'button[aria-label*="Connect"]'],
  moreButton: ['button[aria-label="More actions"]', 'button.artdeco-dropdown__trigger.pvs-profile-actions__overflow-toggle'],
  addNoteButton: ['button[aria-label="Add a note"]', 'button.artdeco-modal__actionbar button:first-child'],
  noteTextarea: ['textarea[name="message"]', 'textarea#custom-message', '.artdeco-modal textarea'],
  sendInviteButton: ['button[aria-label="Send now"]', 'button[aria-label="Send invitation"]', 'button.artdeco-modal__actionbar button.artdeco-button--primary'],
  messageButton: ['button[aria-label*="Message"]', '.pvs-profile-actions__action[aria-label*="Message"]'],
  messageBox: ['div[role="textbox"][aria-label*="Write a message"]', '.msg-form__contenteditable', 'div.msg-form__msg-content-container div[contenteditable="true"]'],
  sendMessageButton: ['button[type="submit"].msg-form__send-button', 'button[aria-label*="Send"]'],
  profileName: ['h1.text-heading-xlarge', 'h1.inline.t-24'],
  profileHeadline: ['div.text-body-medium.break-words'],
  profileLocation: ['span.text-body-small.inline.t-black--light.break-words'],
  profileAbout: ['div.pv-shared-text-with-see-more span[aria-hidden="true"]'],
  profileCompany: ['button[aria-label*="Current company"] span'],
  profileFollowers: ['span.t-bold'],
  connectionDegree: ['span.dist-value', '.distance-badge span'],
  inmailButton: ['button[aria-label*="InMail"]'],
  inmailSubject: ['input[name="subject"]', 'input[placeholder*="Subject"]'],
  inmailBody: ['textarea[name="body"]', 'div[role="textbox"]'],
  sendInmailButton: ['button[type="submit"]'],
  pendingLabel: ['button[aria-label*="Pending"]'],
  weeklyLimitModal: ['div.ip-fuse-limit-alert'],
  captchaChallenge: ['#captcha-challenge', 'iframe[src*="captcha"]', '.challenge-dialog'],
  searchResultCards: ['li.reusable-search__result-container', '.search-results-container li'],
  searchResultName: ['span.entity-result__title-text a span[aria-hidden="true"]'],
  searchResultHeadline: ['div.entity-result__primary-subtitle'],
  searchResultLocation: ['div.entity-result__secondary-subtitle'],
  searchResultLink: ['span.entity-result__title-text a'],
  nextPageButton: ['button[aria-label="Next"]', 'button.artdeco-pagination__button--next']
};

// ── Helpers ──
function $q(s, p = document) { for (const sel of (Array.isArray(s) ? s : [s])) { try { const e = p.querySelector(sel); if (e) return e; } catch {} } return null; }
function $$q(s, p = document) { for (const sel of (Array.isArray(s) ? s : [s])) { try { const e = p.querySelectorAll(sel); if (e.length) return [...e]; } catch {} } return []; }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function waitFor(selectors, timeout = 20000) {
  return new Promise((resolve, reject) => {
    const el = $q(selectors); if (el) return resolve(el);
    const obs = new MutationObserver(() => { const el = $q(selectors); if (el) { obs.disconnect(); resolve(el); } });
    obs.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => { obs.disconnect(); reject(new Error('Element not found')); }, timeout);
  });
}
async function typeText(el, text) {
  el.focus();
  for (const c of text) { el.textContent += c; el.dispatchEvent(new InputEvent('input', { bubbles: true, data: c })); await sleep(50 + Math.random() * 100); }
}
async function typeInTextarea(el, text) {
  el.focus(); el.value = '';
  for (const c of text) { el.value += c; el.dispatchEvent(new Event('input', { bubbles: true })); await sleep(50 + Math.random() * 100); }
}

// ── Commands ──

async function ping() {
  const loggedIn = isLoggedIn();
  const captcha = isCaptchaVisible();
  return { success: true, ready: true, loggedIn: loggedIn && !captcha, captcha, url: window.location.href };
}

async function checkLoginStatus() {
  const loggedIn = isLoggedIn();
  const captcha = isCaptchaVisible();
  return { success: true, loggedIn: loggedIn && !captcha, captcha };
}

// Robust login detection — works with LinkedIn's obfuscated 2025+ DOM
function isLoggedIn() {
  // Check for global nav (present on all logged-in pages)
  if (document.querySelector('img.global-nav__me-photo')) return true;
  if (document.querySelector('.feed-identity-module')) return true;
  // Check for any nav element with profile image
  if (document.querySelector('img[alt*="Photo of"]')) return true;
  if (document.querySelector('img[alt*="photo"]')) return true;
  // Check for nav bar with messaging/notifications
  if (document.querySelector('a[href*="/messaging/"]')) return true;
  if (document.querySelector('a[href*="/notifications/"]')) return true;
  // Check if we're on linkedin.com and not on login/signup pages
  const url = window.location.href;
  if (url.includes('/login') || url.includes('/signup') || url.includes('/checkpoint/')) return false;
  // If on linkedin.com/in/ or /search/ or /feed, assume logged in
  if (url.includes('/in/') || url.includes('/search/') || url.includes('/feed')) return true;
  return false;
}

// CAPTCHA detection — only flag actual visible challenge pages
function isCaptchaVisible() {
  // Check if we're on a challenge/checkpoint URL
  if (window.location.href.includes('/checkpoint/challenge')) return true;
  // Check for visible CAPTCHA elements
  const challenge = document.querySelector('#captcha-challenge');
  if (challenge && challenge.offsetParent !== null) return true;
  const dialog = document.querySelector('.challenge-dialog');
  if (dialog && dialog.offsetParent !== null) return true;
  // Don't count hidden iframes
  return false;
}

// Debug: inspect the page structure for search results
async function debugPage() {
  await sleep(1000);
  const url = window.location.href;
  const title = document.title;
  // Try multiple possible selectors for search result containers
  const tests = {
    'li.reusable-search__result-container': document.querySelectorAll('li.reusable-search__result-container').length,
    '.search-results-container li': document.querySelectorAll('.search-results-container li').length,
    'div.search-results-container': document.querySelectorAll('div.search-results-container').length,
    'ul.reusable-search__entity-result-list': document.querySelectorAll('ul.reusable-search__entity-result-list').length,
    'li[class*="reusable-search"]': document.querySelectorAll('li[class*="reusable-search"]').length,
    'div[class*="entity-result"]': document.querySelectorAll('div[class*="entity-result"]').length,
    'span[class*="entity-result__title"]': document.querySelectorAll('span[class*="entity-result__title"]').length,
    'div[data-view-name="search-entity-result-universal-template"]': document.querySelectorAll('div[data-view-name="search-entity-result-universal-template"]').length,
    'li.artdeco-list__item': document.querySelectorAll('li.artdeco-list__item').length,
    'div.mb1 a[href*="/in/"]': document.querySelectorAll('div.mb1 a[href*="/in/"]').length,
    'a[href*="/in/"]': document.querySelectorAll('a[href*="/in/"]').length,
    'span[dir="ltr"]': document.querySelectorAll('span[dir="ltr"]').length,
  };
  // Get first few link hrefs that contain /in/
  const profileLinks = [...document.querySelectorAll('a[href*="/in/"]')].slice(0, 5).map(a => {
    // Walk up the DOM to find ancestor structure
    const ancestors = [];
    let el = a;
    for (let i = 0; i < 8 && el; i++) { ancestors.push(el.tagName + '.' + (el.className || '').substring(0, 40)); el = el.parentElement; }
    const li = a.closest('li');
    return { href: a.href, text: a.textContent.trim().substring(0, 50), parent: a.parentElement?.tagName, hasLi: !!li, liDepth: li ? ancestors.findIndex(x => x.startsWith('LI')) : -1, ancestors: ancestors.slice(0, 6) };
  });
  // Get main content area classes
  const mainClasses = document.querySelector('main')?.className || 'no main element';
  // Get all list items in search area
  const lists = [...document.querySelectorAll('ul')].filter(ul => ul.querySelectorAll('li').length > 3).map(ul => ({ class: ul.className.substring(0, 80), liCount: ul.querySelectorAll('li').length })).slice(0, 5);
  return { success: true, debug: true, url, title, selectorTests: tests, profileLinks, mainClasses, lists };
}

// Scrape search results on the CURRENT page (no navigation — background handles that)
// LinkedIn 2025+: No semantic classes, no <li> cards. All obfuscated divs.
// Strategy: find all a[href*="/in/"] links, group by URL, extract from ancestors.
async function scrapeCurrentPage() {
  if ($q(S.captchaChallenge)) return { success: false, error: 'CAPTCHA' };
  await sleep(2000);

  const allLinks = [...document.querySelectorAll('a[href*="/in/"]')];
  if (!allLinks.length) return { success: true, profiles: [], hasNextPage: false };

  // LinkedIn search results 2025: each result card is an <a> tag wrapping a div structure.
  // There are 2 links per profile: a big wrapper <a> (with full card text) and a smaller
  // name-only <a> inside it. We want the wrapper <a> to get the full card text.
  const urlToCard = new Map();
  for (const a of allLinks) {
    const url = a.href.split('?')[0];
    if (!url.includes('/in/')) continue;
    // Get the outermost <a> for this profile (the card wrapper)
    // It's the one whose textContent is longest (contains name + headline + location)
    const existing = urlToCard.get(url);
    if (!existing || a.textContent.length > existing.textContent.length) {
      urlToCard.set(url, a);
    }
  }

  const profiles = [];
  for (const [profileUrl, cardLink] of urlToCard) {
    try {
      const fullText = cardLink.textContent.trim();
      if (!fullText || fullText.length < 3) continue;

      // Also find the short name-only link (smallest text for this URL)
      let name = '';
      for (const a of allLinks) {
        if (a.href.split('?')[0] === profileUrl) {
          const t = a.textContent.trim();
          if (t && t.length > 1 && t.length < 60) {
            if (!name || t.length < name.length) name = t;
          }
        }
      }
      name = name.replace(/\s*[•·]\s*(1st|2nd|3rd|[\d]+\+?).*/g, '').trim();
      if (!name || name === 'LinkedIn Member') continue;

      // Parse the full card text to extract headline and location
      // Format is usually: "Name • 2nd\nHeadline text\nLocation\n..."
      // Split by newlines and bullet separators
      const lines = fullText.split(/\n/).map(l => l.trim()).filter(l => l && l.length > 1);

      const degree = fullText.includes('2nd') ? '2nd' : fullText.includes('3rd') ? '3rd' : '1st';

      // Find headline: first substantial line that isn't the name and isn't a button label
      let headline = '';
      let location = '';
      const skipWords = ['connect', 'message', 'follow', 'pending', 'send', 'inmailmessage', 'view profile'];
      for (const line of lines) {
        const lower = line.toLowerCase();
        // Skip the name line, degree markers, button labels
        if (line === name || lower.includes(name.toLowerCase())) continue;
        if (/^(1st|2nd|3rd|•|·)/.test(line)) continue;
        if (skipWords.some(w => lower.startsWith(w))) continue;
        if (line.length < 3) continue;

        // Location heuristic
        const isLocation = /\b(area|india|states|united|york|francisco|london|bangalore|mumbai|delhi|remote|california|texas|chicago|boston|seattle|singapore|dubai|canada|australia|germany|france|uk|england)\b/i.test(line) || /^[A-Z][a-z]+,\s[A-Z]/.test(line);
        if (isLocation && !location) { location = line.substring(0, 100); continue; }

        // Headline: first non-name, non-location text that's substantial
        if (!headline && line.length > 5) { headline = line.substring(0, 200); }
      }

      profiles.push({ name, headline, location, profileUrl, degree });
    } catch {}
  }

  const next = document.querySelector('button[aria-label="Next"]');
  return { success: true, profiles, count: profiles.length, hasNextPage: !!(next && !next.disabled) };
}

// Legacy searchProfiles — kept for backward compat but now just scrapes current page
async function searchProfiles(args) {
  return await scrapeCurrentPage();
}

async function deepScanProfile(args) {
  // Background script handles navigation via _skipNavigation flag
  const name = $q(S.profileName)?.textContent?.trim() || '';
  const headline = $q(S.profileHeadline)?.textContent?.trim() || '';
  const location = $q(S.profileLocation)?.textContent?.trim() || '';
  const about = $q(S.profileAbout)?.textContent?.trim() || '';
  const company = $q(S.profileCompany)?.textContent?.trim() || '';
  const degree = $q(S.connectionDegree)?.textContent?.trim() || '';
  const experience = $$q('li.artdeco-list__item section div.display-flex').slice(0, 3).map(e => e.textContent.trim().substring(0, 200));
  const posts = $$q('div.feed-shared-update-v2__description').slice(0, 3).map(e => e.textContent.trim().substring(0, 300));
  const fEl = [...document.querySelectorAll('span')].find(e => e.textContent.includes('followers'));
  return { success: true, profile: { name, headline, location, about, company, degree, experience, posts, followers: fEl ? fEl.textContent.trim() : '' } };
}

async function sendConnectionRequest(args) {
  const { note } = args;
  // Background already navigated to the profile
  if ($q(S.weeklyLimitModal)) return { success: false, error: 'WEEKLY_LIMIT', message: 'Weekly invitation limit reached' };
  let btn = $q(S.connectButton);
  if (!btn) { const more = $q(S.moreButton); if (more) { more.click(); await sleep(800); btn = $q(S.connectButton); } }
  if (!btn) {
    if ($q(S.messageButton)) return { success: false, error: 'ALREADY_CONNECTED', message: 'Already connected' };
    if ($q(S.pendingLabel)) return { success: false, error: 'PENDING', message: 'Request already pending' };
    return { success: false, error: 'NO_CONNECT_BUTTON', message: 'Connect button not found' };
  }
  btn.click(); await sleep(1000);
  if (note) {
    const ab = $q(S.addNoteButton);
    if (ab) { ab.click(); await sleep(800); const ta = await waitFor(S.noteTextarea, 5000); await typeInTextarea(ta, note.length > 300 ? note.substring(0, 295) + '...' : note); await sleep(500); }
  }
  const send = await waitFor(S.sendInviteButton, 5000); send.click(); await sleep(1000);
  if ($q(S.weeklyLimitModal)) return { success: false, error: 'WEEKLY_LIMIT', message: 'Weekly limit reached' };
  return { success: true, action: 'connection_sent' };
}

async function sendInMail(args) {
  const { subject, body } = args;
  const btn = $q(S.inmailButton);
  if (!btn) return { success: false, error: 'NO_INMAIL_BUTTON', message: 'InMail not found. Premium required.' };
  btn.click(); await sleep(1500);
  if (subject) { const s = await waitFor(S.inmailSubject, 5000); s.value = subject; s.dispatchEvent(new Event('input', { bubbles: true })); await sleep(300); }
  const b = await waitFor(S.inmailBody, 5000);
  if (b.tagName === 'TEXTAREA') await typeInTextarea(b, body); else await typeText(b, body);
  await sleep(500);
  const send = await waitFor(S.sendInmailButton, 5000); send.click(); await sleep(1000);
  return { success: true, action: 'inmail_sent' };
}

async function checkConnectionStatus(args) {
  if ($q(S.messageButton)) return { success: true, status: 'accepted' };
  if ($q(S.pendingLabel) || document.body.textContent.includes('Pending')) return { success: true, status: 'pending' };
  if ($q(S.connectButton)) return { success: true, status: 'not_connected' };
  return { success: true, status: 'unknown' };
}

async function sendMessage(args) {
  const { message } = args;
  const btn = $q(S.messageButton);
  if (!btn) return { success: false, error: 'NO_MESSAGE_BUTTON', message: 'Not connected?' };
  btn.click(); await sleep(1500);
  const box = await waitFor(S.messageBox, 10000); await typeText(box, message); await sleep(500);
  const send = await waitFor(S.sendMessageButton, 5000); send.click(); await sleep(1000);
  return { success: true, action: 'message_sent' };
}

// ── Message Listener ──
window.__10X_LISTENER = function(msg, sender, sendResponse) {
  if (msg.type !== '10X_COMMAND') return;
  const handlers = {
    ping, checkLoginStatus,
    scrapeCurrentPage,
    searchProfiles,
    debugPage,
    deepScan: deepScanProfile,
    sendConnection: sendConnectionRequest,
    sendInMail,
    checkConnectionStatus,
    checkAcceptance: checkConnectionStatus,
    sendMessage,
    detectWeeklyLimit: async () => ({ success: true, limitReached: !!$q(S.weeklyLimitModal) })
  };
  const fn = handlers[msg.command];
  if (!fn) { sendResponse({ success: false, error: 'Unknown command: ' + msg.command }); return; }
  fn(msg.args).then(sendResponse).catch(e => sendResponse({ success: false, error: e.message }));
  return true;
};
chrome.runtime.onMessage.addListener(window.__10X_LISTENER);
