// Guard against multiple injections — remove old listener if re-injected
if(window.__10X_LISTENER){try{chrome.runtime.onMessage.removeListener(window.__10X_LISTENER)}catch{}}
window.__10X_CONTENT_READY=true;
const S={
  connectButton:['button[aria-label*="Invite"][aria-label*="connect"]','button.pvs-profile-actions__action[aria-label*="Connect"]','button[aria-label*="Connect"]'],
  moreButton:['button[aria-label="More actions"]','button.artdeco-dropdown__trigger.pvs-profile-actions__overflow-toggle'],
  addNoteButton:['button[aria-label="Add a note"]','button.artdeco-modal__actionbar button:first-child'],
  noteTextarea:['textarea[name="message"]','textarea#custom-message','.artdeco-modal textarea'],
  sendInviteButton:['button[aria-label="Send now"]','button[aria-label="Send invitation"]','button.artdeco-modal__actionbar button.artdeco-button--primary'],
  messageButton:['button[aria-label*="Message"]','.pvs-profile-actions__action[aria-label*="Message"]'],
  messageBox:['div[role="textbox"][aria-label*="Write a message"]','.msg-form__contenteditable','div.msg-form__msg-content-container div[contenteditable="true"]'],
  sendMessageButton:['button[type="submit"].msg-form__send-button','button[aria-label*="Send"]'],
  profileName:['h1.text-heading-xlarge','h1.inline.t-24'],
  profileHeadline:['div.text-body-medium.break-words'],
  profileLocation:['span.text-body-small.inline.t-black--light.break-words'],
  profileAbout:['div.pv-shared-text-with-see-more span[aria-hidden="true"]'],
  profileCompany:['button[aria-label*="Current company"] span'],
  profileFollowers:['span.t-bold'],
  connectionDegree:['span.dist-value','.distance-badge span'],
  inmailButton:['button[aria-label*="InMail"]'],
  inmailSubject:['input[name="subject"]','input[placeholder*="Subject"]'],
  inmailBody:['textarea[name="body"]','div[role="textbox"]'],
  sendInmailButton:['button[type="submit"]'],
  pendingLabel:['button[aria-label*="Pending"]'],
  weeklyLimitModal:['div.ip-fuse-limit-alert'],
  captchaChallenge:['#captcha-challenge','iframe[src*="captcha"]','.challenge-dialog'],
  searchResultCards:['li.reusable-search__result-container','.search-results-container li'],
  searchResultName:['span.entity-result__title-text a span[aria-hidden="true"]'],
  searchResultHeadline:['div.entity-result__primary-subtitle'],
  searchResultLocation:['div.entity-result__secondary-subtitle'],
  searchResultLink:['span.entity-result__title-text a'],
  nextPageButton:['button[aria-label="Next"]','button.artdeco-pagination__button--next']
};

function $q(s,p=document){for(const sel of(Array.isArray(s)?s:[s])){try{const e=p.querySelector(sel);if(e)return e}catch{}}return null}
function $$q(s,p=document){for(const sel of(Array.isArray(s)?s:[s])){try{const e=p.querySelectorAll(sel);if(e.length)return[...e]}catch{}}return[]}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function waitFor(selectors,timeout=20000){return new Promise((resolve,reject)=>{const el=$q(selectors);if(el)return resolve(el);const obs=new MutationObserver(()=>{const el=$q(selectors);if(el){obs.disconnect();resolve(el)}});obs.observe(document.body,{childList:true,subtree:true});setTimeout(()=>{obs.disconnect();reject(new Error("Element not found"))},timeout)})}
async function typeText(el,text){el.focus();for(const c of text){el.textContent+=c;el.dispatchEvent(new InputEvent("input",{bubbles:true,data:c}));await sleep(50+Math.random()*100)}}
async function typeInTextarea(el,text){el.focus();el.value="";for(const c of text){el.value+=c;el.dispatchEvent(new Event("input",{bubbles:true}));await sleep(50+Math.random()*100)}}
async function navigateTo(url){window.location.href=url;await new Promise(r=>{const ch=setInterval(()=>{if(document.readyState==="complete"){clearInterval(ch);r()}},200)});await sleep(1000+Math.random()*1000)}

async function checkLoginStatus(){
  const ok=!!document.querySelector("img.global-nav__me-photo")||!!document.querySelector(".feed-identity-module")||window.location.hostname==="www.linkedin.com";
  const captcha=!!$q(S.captchaChallenge);
  return{success:true,loggedIn:ok&&!captcha,captcha};
}

async function searchProfiles(args){
  const{filters={},maxPages=10}=args;
  const params=new URLSearchParams();
  if(filters.keywords)params.set("keywords",filters.keywords);
  if(filters.industry)params.set("industry",filters.industry);
  if(filters.location)params.set("geoUrn",filters.location);
  if(filters.company)params.set("company",filters.company);
  const baseUrl="https://www.linkedin.com/search/results/people/?"+params;
  const all=[];
  for(let page=1;page<=maxPages;page++){
    await navigateTo(page===1?baseUrl:baseUrl+"&page="+page);
    await sleep(2000+Math.random()*1000);
    if($q(S.captchaChallenge))return{success:false,error:"CAPTCHA detected",profiles:all};
    const cards=$$q(S.searchResultCards);if(!cards.length)break;
    for(const card of cards){
      try{
        const nameEl=$q(S.searchResultName,card),linkEl=$q(S.searchResultLink,card);
        if(!nameEl||!linkEl)continue;
        const headlineEl=$q(S.searchResultHeadline,card),locationEl=$q(S.searchResultLocation,card);
        all.push({name:nameEl.textContent.trim(),headline:headlineEl?headlineEl.textContent.trim():"",location:locationEl?locationEl.textContent.trim():"",profileUrl:linkEl.href.split("?")[0],degree:card.textContent.includes("2nd")?"2nd":card.textContent.includes("3rd")?"3rd":"1st"});
      }catch{}
    }
    const next=$q(S.nextPageButton);if(!next||next.disabled)break;
  }
  return{success:true,profiles:all,count:all.length};
}

async function deepScanProfile(args){
  const{profileUrl}=args;
  if(profileUrl&&!window.location.href.includes(profileUrl.replace("https://www.linkedin.com",""))){await navigateTo(profileUrl);await sleep(2000)}
  const name=$q(S.profileName)?.textContent?.trim()||"";
  const headline=$q(S.profileHeadline)?.textContent?.trim()||"";
  const location=$q(S.profileLocation)?.textContent?.trim()||"";
  const about=$q(S.profileAbout)?.textContent?.trim()||"";
  const company=$q(S.profileCompany)?.textContent?.trim()||"";
  const degree=$q(S.connectionDegree)?.textContent?.trim()||"";
  const experience=$$q("li.artdeco-list__item section div.display-flex").slice(0,3).map(e=>e.textContent.trim().substring(0,200));
  const posts=$$q("div.feed-shared-update-v2__description").slice(0,3).map(e=>e.textContent.trim().substring(0,300));
  const fEl=[...document.querySelectorAll("span")].find(e=>e.textContent.includes("followers"));
  return{success:true,profile:{name,headline,location,about,company,degree,experience,posts,followers:fEl?fEl.textContent.trim():""}};
}

async function sendConnectionRequest(args){
  const{profileUrl,note}=args;
  if(profileUrl){await navigateTo(profileUrl);await sleep(2000)}
  if($q(S.weeklyLimitModal))return{success:false,error:"WEEKLY_LIMIT",message:"Weekly invitation limit reached"};
  let btn=$q(S.connectButton);
  if(!btn){const more=$q(S.moreButton);if(more){more.click();await sleep(800);btn=$q(S.connectButton)}}
  if(!btn){
    if($q(S.messageButton))return{success:false,error:"ALREADY_CONNECTED",message:"Already connected"};
    if($q(S.pendingLabel))return{success:false,error:"PENDING",message:"Request already pending"};
    return{success:false,error:"NO_CONNECT_BUTTON",message:"Connect button not found"};
  }
  btn.click();await sleep(1000);
  if(note){
    const ab=$q(S.addNoteButton);
    if(ab){ab.click();await sleep(800);const ta=await waitFor(S.noteTextarea,5000);await typeInTextarea(ta,note.length>300?note.substring(0,295)+"...":note);await sleep(500)}
  }
  const send=await waitFor(S.sendInviteButton,5000);send.click();await sleep(1000);
  if($q(S.weeklyLimitModal))return{success:false,error:"WEEKLY_LIMIT",message:"Weekly limit reached"};
  return{success:true,action:"connection_sent"};
}

async function sendInMail(args){
  const{profileUrl,subject,body}=args;
  if(profileUrl){await navigateTo(profileUrl);await sleep(2000)}
  const btn=$q(S.inmailButton);
  if(!btn)return{success:false,error:"NO_INMAIL_BUTTON",message:"InMail not found. Premium required."};
  btn.click();await sleep(1500);
  if(subject){const s=await waitFor(S.inmailSubject,5000);s.value=subject;s.dispatchEvent(new Event("input",{bubbles:true}));await sleep(300)}
  const b=await waitFor(S.inmailBody,5000);
  if(b.tagName==="TEXTAREA")await typeInTextarea(b,body);else await typeText(b,body);
  await sleep(500);
  const send=await waitFor(S.sendInmailButton,5000);send.click();await sleep(1000);
  return{success:true,action:"inmail_sent"};
}

async function checkConnectionStatus(args){
  const{profileUrl}=args;
  if(profileUrl){await navigateTo(profileUrl);await sleep(2000)}
  if($q(S.messageButton))return{success:true,status:"accepted"};
  if($q(S.pendingLabel)||document.body.textContent.includes("Pending"))return{success:true,status:"pending"};
  if($q(S.connectButton))return{success:true,status:"not_connected"};
  return{success:true,status:"unknown"};
}

async function sendMessage(args){
  const{profileUrl,message}=args;
  if(profileUrl){await navigateTo(profileUrl);await sleep(2000)}
  const btn=$q(S.messageButton);
  if(!btn)return{success:false,error:"NO_MESSAGE_BUTTON",message:"Not connected?"};
  btn.click();await sleep(1500);
  const box=await waitFor(S.messageBox,10000);await typeText(box,message);await sleep(500);
  const send=await waitFor(S.sendMessageButton,5000);send.click();await sleep(1000);
  return{success:true,action:"message_sent"};
}

async function ping(){const l=await checkLoginStatus();return{success:true,ready:true,loggedIn:l.loggedIn}}

window.__10X_LISTENER=function(msg,sender,sendResponse){
  if(msg.type!=="10X_COMMAND")return;
  const h={ping,checkLoginStatus,searchProfiles,deepScan:deepScanProfile,sendConnection:sendConnectionRequest,sendInMail,checkConnectionStatus,checkAcceptance:checkConnectionStatus,sendMessage,detectWeeklyLimit:async()=>({success:true,limitReached:!!$q(S.weeklyLimitModal)})};
  const fn=h[msg.command];
  if(!fn){sendResponse({success:false,error:"Unknown: "+msg.command});return}
  fn(msg.args).then(sendResponse).catch(e=>sendResponse({success:false,error:e.message}));
  return true;
};
chrome.runtime.onMessage.addListener(window.__10X_LISTENER);
