# Workflow Command - Visual Canvas First! 🎨

Create and execute multi-platform outreach workflows using the visual canvas.

**Developed by 10x.in**

## 🎯 Simple 4-Step Process

```
1. Design Visually → 2. User Approves → 3. Save with ID → 4. Execute
```

## Usage

### Create Workflow (Visual Canvas)

```
/workflow create for <target audience>
```

**Example:**
```
/workflow create for AI founders on LinkedIn and Twitter
```

**What happens:**
1. ✅ Canvas opens at **http://localhost:3000**
2. ✅ Visual workflow appears with nodes automatically
3. ✅ User reviews and approves the design
4. ✅ User clicks "Save" → Gets unique ID (e.g., `a3f7c921`)
5. ✅ Status: `pending` (ready to run)

### Run Workflow

```
/workflow run <workflow_id>
```

or

```
/workflow run latest
```

**Example:**
```
/workflow run a3f7c921
```

### Check Status

```
/workflow status <workflow_id>
```

### List All Workflows

```
/workflow list
```

Shows table with ID, Name, Status, Platforms, Nodes, Created date.

### Pause/Resume

```
/workflow pause <workflow_id>
/workflow resume <workflow_id>
```

## 📍 Ports (IMPORTANT!)

- **Canvas Frontend**: http://localhost:3000 (TLDraw)
- **WebSocket**: ws://localhost:3001/ws (Commands)
- **API**: http://localhost:3000/api (REST)

## 🔧 How It Works

### 1. Canvas Design Phase
- Visual drag-and-drop interface
- Add nodes: Discovery, LinkedIn, Twitter, Instagram, Email, Delay
- Connect nodes with arrows to define flow
- See complete workflow before executing

### 2. Workflow Database
- Each workflow gets unique 8-character ID
- Status tracking: `pending`, `running`, `completed`, `failed`, `paused`
- Execution history with timestamps
- Full audit trail

### 3. Execution Phase
- Reads canvas JSON
- Executes nodes in order following connections
- Updates status in real-time
- Logs every action

### 4. Integration
- **Browser Extension**: `./browser-extension/` for LinkedIn/Twitter/Instagram
- **Exa.ai MCP**: Intelligent people discovery
- **Gmail API**: Email sending
- **Rate Limiting**: Automatic safe delays

## 📊 Workflow Status Codes

| Status | Meaning |
|--------|---------|
| `pending` | Saved, ready to run |
| `running` | Currently executing |
| `completed` | Successfully finished |
| `failed` | Error occurred |
| `paused` | Execution paused by user |

## 🚀 Quick Example

```bash
# User says:
/workflow create for startup founders

# System:
✅ Canvas opened at http://localhost:3000
✅ Workflow created with 6 nodes
✅ Review workflow → Click "Save"
✅ Workflow ID: a3f7c921
✅ Status: pending

# User says:
/workflow run a3f7c921

# System:
✅ Status: running
✅ Executing Discovery...
✅ Found 50 startup founders
✅ Executing LinkedIn View Profile...
✅ Viewed 50 profiles
... (continues)
✅ Status: completed
```

## 🗂️ Files

- **Database**: `./output/workflows/workflow_db.json`
- **Workflows**: `./output/workflows/<workflow_id>.json`
- **Logs**: `./output/logs/<workflow_id>_<timestamp>.log`

## ⚠️ Important Rules

1. **Canvas First**: ALWAYS design in canvas first
2. **User Approval**: User MUST approve before execution
3. **Port 3000**: Canvas frontend on port 3000
4. **Port 3001**: WebSocket on port 3001
5. **Unique IDs**: Every workflow gets unique ID
6. **Status Tracking**: All workflows tracked in database

---

**Powered by TLDraw + ClaudeKit Extension + Exa.ai MCP**
**Developed by 10x.in** 🔥
