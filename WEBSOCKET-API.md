# WebSocket API Reference for Claude Code

## Connection

**Endpoint**: `ws://localhost:3000/ws`

**Auto-connection**: Canvas connects automatically on load

**Connection States**:
- ✅ Connected - Canvas is live and receiving commands
- ⏳ Reconnecting - Will retry in 60 seconds
- ❌ Disconnected - App closed or network issue

---

## Commands via WebSocket

All commands sent through WebSocket are executed in real-time on the canvas.

### 1. Clear Canvas

**Command**:
```json
{
  "type": "clear"
}
```

**Effect**: Removes all nodes and connections from canvas

**Use Case**: Starting a new workflow from scratch

---

### 2. Add Node

**Command**:
```json
{
  "type": "add-node",
  "payload": {
    "id": "node-1",
    "nodeType": "skill-node",
    "skillType": "linkedin",
    "label": "LinkedIn Connect",
    "description": "Send connection request",
    "x": 200,
    "y": 200,
    "config": {
      "message": "Hi {name}, let's connect!"
    }
  }
}
```

**Required Fields**:
- `id` - Unique identifier (used for connections)
- `label` - Display name
- `description` - What this node does
- `x`, `y` - Canvas position

**Optional Fields**:
- `nodeType` - Default: "skill-node"
- `skillType` - Default: "discovery"
- `config` - Node-specific configuration

**Skill Types**:
- `discovery` - Find people using Exa AI
- `linkedin` - LinkedIn automation
- `twitter` - Twitter/X automation
- `instagram` - Instagram automation
- `gmail` - Email sending
- `workflow` - Workflow control
- `template` - Template usage
- `audience` - Audience management
- `campaign` - Campaign tracking

**Node Colors** (auto-applied):
- Discovery: Purple (#9333ea)
- LinkedIn: Blue (#0077b5)
- Twitter: Light Blue (#1da1f2)
- Instagram: Pink (#e4405f)
- Gmail: Red (#ea4335)
- Workflow: Green (#10b981)

---

### 3. Add Connection

**Command**:
```json
{
  "type": "add-connection",
  "payload": {
    "from": "node-1",
    "to": "node-2",
    "fromX": 400,
    "fromY": 260,
    "toX": 600,
    "toY": 260
  }
}
```

**Required Fields**:
- `from` - Source node ID
- `to` - Target node ID
- `fromX`, `fromY` - Connection start point
- `toX`, `toY` - Connection end point

**Note**: Branching supported! One output can connect to multiple inputs.

**Visual Feedback**:
- Green line with arrow for valid connections
- Bezier curve for smooth appearance
- Delete button on hover

---

### 4. Run Simulation

**Command**:
```json
{
  "type": "run-simulation"
}
```

**Effect**: Triggers step-by-step simulation of workflow execution

**Visual Feedback**:
- Nodes light up as they "execute"
- Connections show flow animation
- Status indicators change color

---

## Batch Commands

For building complex workflows, send multiple commands at once:

**HTTP Endpoint**: `POST http://localhost:3000/api/canvas/commands/batch`

**Request Body**:
```json
{
  "commands": [
    {
      "type": "clear"
    },
    {
      "type": "add-node",
      "payload": {
        "id": "discovery-1",
        "skillType": "discovery",
        "label": "Find AI Founders",
        "description": "Search for AI startup founders",
        "x": 100,
        "y": 200
      }
    },
    {
      "type": "add-node",
      "payload": {
        "id": "linkedin-1",
        "skillType": "linkedin",
        "label": "View Profile",
        "description": "View their LinkedIn profile",
        "x": 400,
        "y": 200
      }
    },
    {
      "type": "add-connection",
      "payload": {
        "from": "discovery-1",
        "to": "linkedin-1",
        "fromX": 300,
        "fromY": 260,
        "toX": 400,
        "toY": 260
      }
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "commandCount": 4,
  "clients": 1
}
```

**Timing**: Commands execute with 300ms delay between each for visual effect

---

## Building Workflows via WebSocket

### Example: LinkedIn Outreach Workflow

**Step 1**: Clear canvas
```json
{
  "type": "clear"
}
```

**Step 2**: Add discovery node
```json
{
  "type": "add-node",
  "payload": {
    "id": "discovery",
    "skillType": "discovery",
    "label": "Find AI Founders",
    "x": 100,
    "y": 200,
    "config": {
      "query": "AI startup founders in San Francisco"
    }
  }
}
```

**Step 3**: Add LinkedIn view node
```json
{
  "type": "add-node",
  "payload": {
    "id": "linkedin-view",
    "skillType": "linkedin",
    "label": "View Profile",
    "x": 400,
    "y": 200
  }
}
```

**Step 4**: Add LinkedIn like node
```json
{
  "type": "add-node",
  "payload": {
    "id": "linkedin-like",
    "skillType": "linkedin",
    "label": "Like Recent Post",
    "x": 700,
    "y": 200
  }
}
```

**Step 5**: Add LinkedIn connect node
```json
{
  "type": "add-node",
  "payload": {
    "id": "linkedin-connect",
    "skillType": "linkedin",
    "label": "Send Connection",
    "x": 1000,
    "y": 200,
    "config": {
      "message": "Hi {name}, impressed by your work in AI!"
    }
  }
}
```

**Step 6**: Connect the nodes
```json
{
  "type": "add-connection",
  "payload": { "from": "discovery", "to": "linkedin-view", "fromX": 300, "fromY": 260, "toX": 400, "toY": 260 }
}
```

```json
{
  "type": "add-connection",
  "payload": { "from": "linkedin-view", "to": "linkedin-like", "fromX": 600, "fromY": 260, "toX": 700, "toY": 260 }
}
```

```json
{
  "type": "add-connection",
  "payload": { "from": "linkedin-like", "to": "linkedin-connect", "fromX": 900, "fromY": 260, "toX": 1000, "toY": 260 }
}
```

---

## Node Positioning Guidelines

### Horizontal Layout (Recommended):
```
[Node 1] ---> [Node 2] ---> [Node 3]
  x:100        x:400        x:700
  y:200        y:200        y:200
```

**Spacing**: 300px between nodes horizontally

### Vertical Layout:
```
[Node 1]
   |
   v
[Node 2]
   |
   v
[Node 3]
```

**Spacing**: 200px between nodes vertically

### Branching Layout:
```
                [Node 2]
               /
[Node 1] -----
               \
                [Node 3]
```

**Positioning**:
- Node 1: x:100, y:300
- Node 2: x:400, y:200
- Node 3: x:400, y:400

---

## Canvas Coordinate System

**Origin**: Top-left corner (0, 0)

**Viewport**: Infinite canvas (pan and zoom enabled)

**Node Dimensions**:
- Default width: 200px
- Default height: 120px

**Connection Points**:
- **Input**: Left side of node, center vertically
- **Output**: Right side of node, center vertically

**Calculating Connection Positions**:
```javascript
// From node
fromX = node.x + 200  // Right edge
fromY = node.y + 60   // Center vertically

// To node
toX = node.x          // Left edge
toY = node.y + 60     // Center vertically
```

---

## WebSocket Message Flow

### Client → Server (User Actions):
- Delete connection (click delete button)
- Move nodes (drag)
- Select nodes (click)
- Run workflow (click Run button)

### Server → Client (Claude Code):
- Add nodes (visual workflow building)
- Add connections (link nodes)
- Clear canvas (start fresh)
- Run simulation (preview execution)

### Bi-directional:
- Status updates
- Error messages
- Progress indicators

---

## Error Handling

### Connection Errors:
```json
{
  "type": "error",
  "message": "Connection failed: Invalid node ID"
}
```

### Node Creation Errors:
```json
{
  "type": "error",
  "message": "Node creation failed: Missing required field 'label'"
}
```

### WebSocket Disconnection:
- Client automatically attempts reconnection after 60 seconds
- Commands queued during disconnection
- Fallback to polling API if WebSocket unavailable

---

## Best Practices for Claude Code

### 1. Always Clear Before Building:
```json
{ "type": "clear" }
```
Then build your workflow from scratch.

### 2. Use Descriptive Labels:
```json
"label": "Find AI Founders on LinkedIn"  // Good
"label": "Node 1"                       // Bad
```

### 3. Add Node Descriptions:
```json
"description": "Search for AI startup founders in San Francisco using Exa AI"
```
This helps users understand the workflow.

### 4. Space Nodes Appropriately:
- **Simple workflows**: 300px apart
- **Complex workflows**: 400px+ apart to avoid overlap

### 5. Use Batch Commands:
Send all commands in one batch for complex workflows. The canvas will animate them sequentially.

### 6. Provide Visual Feedback:
```json
{
  "type": "add-node",
  "payload": {
    "label": "✅ Workflow Created!",
    "description": "Your workflow is ready to run"
  }
}
```

---

## Testing Commands

### Test Connection:
```bash
curl http://localhost:3000/api/status
```

**Response**:
```json
{
  "status": "running",
  "clients": 1,
  "commandsQueued": 0,
  "uptime": 3600.5
}
```

### Send Test Command:
```bash
curl -X POST http://localhost:3000/api/canvas/command \
  -H "Content-Type: application/json" \
  -d '{
    "type": "add-node",
    "payload": {
      "id": "test-1",
      "label": "Test Node",
      "description": "Testing WebSocket API",
      "x": 200,
      "y": 200
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "commandId": "cmd-1-1737556800000",
  "clients": 1,
  "broadcast": true
}
```

---

## Complete Example: Building a Multi-Platform Campaign

```javascript
// Claude Code sends this batch command
const workflow = {
  "commands": [
    { "type": "clear" },

    // Discovery
    {
      "type": "add-node",
      "payload": {
        "id": "discovery",
        "skillType": "discovery",
        "label": "Find Tech Influencers",
        "description": "Search for tech influencers with 10k+ followers",
        "x": 100, "y": 300,
        "config": { "query": "tech influencers 10k followers" }
      }
    },

    // LinkedIn Path
    {
      "type": "add-node",
      "payload": {
        "id": "linkedin-view",
        "skillType": "linkedin",
        "label": "View LinkedIn",
        "x": 400, "y": 200
      }
    },
    {
      "type": "add-node",
      "payload": {
        "id": "linkedin-connect",
        "skillType": "linkedin",
        "label": "Connect",
        "x": 700, "y": 200
      }
    },

    // Twitter Path
    {
      "type": "add-node",
      "payload": {
        "id": "twitter-follow",
        "skillType": "twitter",
        "label": "Follow on Twitter",
        "x": 400, "y": 400
      }
    },

    // Connections
    { "type": "add-connection", "payload": { "from": "discovery", "to": "linkedin-view", "fromX": 300, "fromY": 260, "toX": 400, "toY": 260 } },
    { "type": "add-connection", "payload": { "from": "linkedin-view", "to": "linkedin-connect", "fromX": 600, "fromY": 260, "toX": 700, "toY": 260 } },
    { "type": "add-connection", "payload": { "from": "discovery", "to": "twitter-follow", "fromX": 300, "fromY": 340, "toX": 400, "toY": 460 } }
  ]
};

// Send to canvas
fetch('http://localhost:3000/api/canvas/commands/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(workflow)
});
```

**Result**: Beautiful branching workflow with LinkedIn and Twitter paths!

---

## Summary

The WebSocket API enables Claude Code to:
1. ✅ Build workflows visually in real-time
2. ✅ Control every aspect of the canvas
3. ✅ Create complex multi-platform sequences
4. ✅ Provide instant visual feedback
5. ✅ Save workflows with intelligent naming

**Primary Channel**: WebSocket (`ws://localhost:3000/ws`)
**Fallback**: HTTP API (`http://localhost:3000/api/*`)

Happy workflow building! 🚀
