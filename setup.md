# Setup Guide — 10X LinkedIn Outreach

## Step 1: Install the Chrome Extension
1. Open Google Chrome
2. Go to `chrome://extensions`
3. Toggle **Developer mode** ON (top right)
4. Click **Load unpacked**
5. Select the `extension/` folder from this project
6. You should see "10X LinkedIn" with a red "OFF" badge

## Step 2: Log Into LinkedIn
1. Open a new tab
2. Go to linkedin.com
3. Log in with your account
4. Keep this tab open

## Step 3: Start the Server
In Claude Code, the server starts automatically when you use any command.
Or start manually:
```bash
node .claude/scripts/extension_client.js --server
```
The extension badge should turn green ("ON").

## Step 4: Test the Connection
```bash
node .claude/scripts/extension_client.js ping
```
Should return: `{"success": true, "ready": true, "loggedIn": true}`

## Step 5: Start Outreaching
1. `/discover` — Find profiles by industry, role, location
2. `/connect` — Send personalized connection requests
3. `/message` — Follow up with accepted connections

## Troubleshooting

**Badge stays red?**
- Make sure the server is running
- Check that port 3456 is not in use

**"No LinkedIn tab open" error?**
- Open linkedin.com in Chrome
- Make sure you're logged in

**CAPTCHA appeared?**
- Solve it manually in the browser
- Resume your command — it picks up where it left off

**Weekly limit reached?**
- LinkedIn limits ~100 invitations per week
- Wait until next week, or use InMail for premium accounts
