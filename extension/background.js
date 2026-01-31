const SERVER_URL='http://localhost:3456';
const POLL_INTERVAL=500;
let connected=false;

function setBadge(status){
  const config={connected:{text:'ON',color:'#22c55e'},disconnected:{text:'OFF',color:'#ef4444'},busy:{text:'...',color:'#f59e0b'}};
  const c=config[status]||config.disconnected;
  chrome.action.setBadgeText({text:c.text});
  chrome.action.setBadgeBackgroundColor({color:c.color});
}
setBadge('disconnected');

async function poll(){
  try{
    const res=await fetch(SERVER_URL+'/poll',{signal:AbortSignal.timeout(3000)});
    if(!res.ok)throw new Error('HTTP '+res.status);
    if(!connected){connected=true;setBadge('connected');console.log('[10X] Connected')}
    const data=await res.json();
    if(data.command){setBadge('busy');await executeCommand(data)}
  }catch(e){
    if(connected){connected=false;setBadge('disconnected');console.log('[10X] Disconnected')}
  }
}

async function executeCommand(data){
  try{
    const tabs=await chrome.tabs.query({url:'*://*.linkedin.com/*'});
    if(!tabs.length){await postResult(data.id,{success:false,error:'No LinkedIn tab open'});setBadge('connected');return}
    const tab=tabs[0];
    try{await chrome.scripting.executeScript({target:{tabId:tab.id},func:()=>!!window.__10X_CONTENT_READY})}
    catch{await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']});await new Promise(r=>setTimeout(r,500))}
    const result=await chrome.tabs.sendMessage(tab.id,{type:'10X_COMMAND',command:data.command,args:data.args||{},id:data.id});
    await postResult(data.id,result);
    if(result&&result.success)await updateDailyCounts(data.command);
  }catch(e){await postResult(data.id,{success:false,error:e.message})}
  setBadge('connected');
}

async function postResult(id,result){
  try{await fetch(SERVER_URL+'/result',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,result}),signal:AbortSignal.timeout(5000)})}
  catch(e){console.error('[10X] Post failed:',e)}
}

async function updateDailyCounts(command){
  const today=new Date().toISOString().split('T')[0];
  const data=await chrome.storage.local.get('dailyCounts');
  let counts=data.dailyCounts||{};
  if(counts.date!==today)counts={date:today,connections:0,messages:0,inmails:0,scrapes:0};
  const map={sendConnection:'connections',sendMessage:'messages',sendInMail:'inmails',searchProfiles:'scrapes',deepScan:'scrapes'};
  if(map[command])counts[map[command]]++;
  await chrome.storage.local.set({dailyCounts:counts});
}

async function getDailyCounts(){
  const today=new Date().toISOString().split('T')[0];
  const data=await chrome.storage.local.get('dailyCounts');
  let counts=data.dailyCounts||{};
  if(counts.date!==today)counts={date:today,connections:0,messages:0,inmails:0,scrapes:0};
  return counts;
}

chrome.runtime.onMessage.addListener((msg,sender,sendResponse)=>{
  if(msg.type==='10X_GET_STATUS'){getDailyCounts().then(counts=>sendResponse({connected,counts}));return true}
});

setInterval(poll,POLL_INTERVAL);
poll();
