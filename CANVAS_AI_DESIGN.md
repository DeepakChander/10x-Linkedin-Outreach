# Draw Anything and Claude Code Will Do It
## Revolutionary AI-Powered Canvas System Design

**Version**: 1.0
**Date**: 2026-01-22
**Status**: Design Phase

---

## Executive Summary

This document outlines the architecture for transforming the 10x-Team canvas from a **predefined node-based workflow builder** (like n8n) into a **revolutionary AI-powered freeform canvas** where users can:

- Draw flow diagrams with any shapes
- Write prompts and instructions in text boxes
- Upload images with descriptions
- Upload videos with context
- Sketch freehand workflows
- Use sticky notes for ideas
- **Have Claude Code interpret and execute everything**

### The Vision

**User draws → Claude Code interprets → Claude Code executes**

Instead of being limited to predefined "Discovery", "LinkedIn", "Twitter" nodes, users can:
- Draw a rectangle labeled "Find AI founders"
- Draw an arrow to another rectangle saying "Check their recent LinkedIn posts"
- Add a text box: "Send personalized message mentioning their latest article"
- **Claude Code figures out what skills to use and executes it**

---

## Research Findings Summary

### 15+ Comprehensive Web Searches Completed

#### 1. TLDraw SDK & Official Documentation
- **TLDraw 4.3.0** is the latest version (already in use!)
- **Editor API** provides full programmatic control
- **Custom Shapes** via ShapeUtil classes
- **Bindings System** for arrow connections between shapes
- **Examples**: tldraw.dev/examples with custom shapes, tools, styles

#### 2. n8n Workflow UI Patterns
- Node-based interface with drag-drop
- **Resource Mapper** for data transformation
- **Visual node connections** with inputs/outputs
- JSON-based workflow definitions
- Platform uses **node description objects** for UI definition

#### 3. React Flow & Node-Based Editors
- **React Flow** - MIT-licensed library for node UIs
- **Flume** - User-friendly node editor
- **Rete.js** - Visual programming framework
- Nodes are React components with draggable connections

#### 4. AI Canvas Interpretation
- **Jeda.ai** - Transforms napkin sketches → AI Flowcharts
- **Canvas by Thesys** - Sketches → UI designs, AI agent workflows
- **AI-Drawing** - Real-time canvas interpretation + image generation
- **Lucidchart AI** - Text/diagrams → visual workflows
- **DiagramGPT** - Supports flowcharts, ERDs, sequence diagrams

#### 5. Handwritten Flowchart Recognition
- **CNN models** (ResNet, VGGNet) for symbol recognition
- **Faster R-CNN** for object detection in diagrams
- **FlowLearn dataset** for flowchart understanding
- **Engineering diagram digitization** using deep learning

#### 6. Visual Workflow to JSON Conversion
- **Workflow Core** (.NET) - JSON/YAML DSL for workflows
- **NodeJS Workflow Engine** - Config-driven JSON transformations
- **Make.com** - Visual workflows → automated execution
- **JSON Crack** - JSON → interactive graphs

#### 7. LLM Orchestration for Workflows
- **LangChain** - Prompt chaining and orchestration
- **LlamaIndex** - Context-augmented LLM applications
- **WorkflowLLM** - Enhancing workflow orchestration with LLMs
- **Agentic Process Automation** - LLMs automate workflow procedures

#### 8. WebSocket Real-Time Collaboration
- **Socket.io** for React real-time canvas sync
- **Collaborative Whiteboard** with React + WebSockets
- **FastAPI + WebSockets** for backend real-time updates
- **Bidirectional communication** for live canvas updates

#### 9. File Upload & Media Handling
- **react-dropzone** for drag-drop uploads
- **PrimeReact FileUpload** with progress tracking
- Drag images onto canvas with React
- Support for **images, videos, PDFs**

---

## Current System Analysis

### What's Already Built ✅

1. **TLDraw Canvas** (canvas/src/App.tsx)
   - TLDraw 4.3.0 with React 19.2.0
   - Custom `SkillNodeShapeUtil` for workflow nodes
   - Auto-save with localStorage
   - API polling for Claude Code commands (500ms interval)

2. **Skill Nodes** (canvas/src/nodes/SkillNodeShapeUtil.tsx)
   - 9 predefined skill types (discovery, linkedin, twitter, instagram, gmail, workflow, template, audience, campaign)
   - Input/Output ports with drag-to-connect
   - Visual status indicators (idle, running, completed, error)
   - Node configuration support

3. **Workflow Engine** (.claude/skills/workflow-engine/SKILL.md)
   - Multi-phase workflows with rate limiting
   - Professional outreach rules (touch limits, platform delays)
   - Integration with Browser-Use MCP
   - Discovery → Warm-up → Engagement → Outreach sequences

4. **Skills System**
   - 14 skills (discovery-engine, linkedin-adapter, twitter-adapter, instagram-adapter, gmail-adapter, etc.)
   - 158+ templates (LinkedIn, Twitter, Instagram, Email)
   - Team management with multi-user support

5. **Canvas API** (App.tsx lines 172-196)
   - `/api/canvas/commands` - Poll for Claude Code commands
   - Command types: `clear`, `add-node`, `add-connection`, `run-simulation`
   - 300ms delay between commands for visual effect

### What's Missing ❌

1. **Freeform Canvas Elements**
   - No support for generic rectangles, circles, text boxes
   - No support for sticky notes
   - No support for freehand drawings
   - Limited to predefined skill nodes only

2. **Media Upload Nodes**
   - No image upload capability
   - No video upload capability
   - No file attachment system

3. **Prompt/Text Nodes**
   - No dedicated "prompt" node type
   - No rich text editing
   - No markdown support

4. **AI Interpretation Layer**
   - No canvas-to-workflow conversion
   - No LLM-powered shape understanding
   - No intelligent routing from freeform → skills

5. **WebSocket Server**
   - Currently using HTTP polling (inefficient)
   - No bidirectional real-time updates
   - No server → client push capability

---

## New Architecture Design

### 3-Tier System

```
┌──────────────────────────────────────────────────────────────────┐
│                     TIER 1: FREEFORM CANVAS                       │
│  Users draw anything - rectangles, text, arrows, images, videos  │
│                    (TLDraw Standard Shapes)                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│              TIER 2: AI INTERPRETATION LAYER                      │
│   Claude Code analyzes canvas → Converts to executable workflow  │
│          (LLM-powered shape understanding + routing)              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│                TIER 3: SKILL EXECUTION LAYER                      │
│         Maps interpreted workflow → Existing skills               │
│   (discovery-engine, linkedin-adapter, gmail-adapter, etc.)      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tier 1: Enhanced Canvas System

### New Node Types

#### 1. Prompt Node
```typescript
{
  type: 'prompt-node',
  props: {
    text: string,           // User's natural language prompt
    category: 'instruction' | 'question' | 'condition' | 'decision',
    aiInterpretation?: string,  // Claude's understanding
    mappedSkill?: string,   // Skill that will execute this
    priority: number,
  }
}
```

**Visual Design:**
- Yellow sticky note appearance
- Markdown editor support
- AI interpretation preview overlay
- Auto-size based on text

#### 2. Image Node
```typescript
{
  type: 'image-node',
  props: {
    imageUrl: string,       // Data URL or uploaded file URL
    description: string,    // User's text description
    caption?: string,
    aiVisionAnalysis?: string,  // Claude's vision API analysis
    tags: string[],
    useInWorkflow: 'context' | 'attachment' | 'reference',
  }
}
```

**Visual Design:**
- Image preview with rounded corners
- Description text below image
- AI analysis overlay (show/hide)
- Drag-drop upload zone

#### 3. Video Node
```typescript
{
  type: 'video-node',
  props: {
    videoUrl: string,
    description: string,
    thumbnailUrl?: string,
    duration?: number,
    transcript?: string,    // Auto-generated or manual
    keyFrames?: string[],   // AI-extracted key moments
    useInWorkflow: 'demo' | 'reference' | 'attachment',
  }
}
```

**Visual Design:**
- Video player with controls
- Transcript sidebar
- AI key moments timeline
- Upload progress indicator

#### 4. Freeform Text Node
```typescript
{
  type: 'text-node',
  props: {
    text: string,
    fontSize: number,
    fontFamily: string,
    color: string,
    alignment: 'left' | 'center' | 'right',
    isMarkdown: boolean,
    aiParsed?: {
      intent: string,
      entities: string[],
      actions: string[],
    }
  }
}
```

**Visual Design:**
- Rich text editor
- Markdown preview mode
- AI parsing visualization
- Color themes

#### 5. Drawing Node
```typescript
{
  type: 'drawing-node',
  props: {
    strokes: TLDrawStroke[],  // Freehand drawing data
    description?: string,
    aiRecognition?: {
      shapes: string[],       // "flowchart", "diagram", "sketch"
      labels: string[],
      connections: Array<{from: string, to: string}>,
    }
  }
}
```

**Visual Design:**
- Transparent overlay for freehand drawing
- Shape recognition feedback
- Convert-to-shapes button
- AI interpretation overlay

#### 6. Decision Node
```typescript
{
  type: 'decision-node',
  props: {
    condition: string,
    trueAction: string,
    falseAction: string,
    evaluationType: 'ai' | 'rule' | 'manual',
  }
}
```

**Visual Design:**
- Diamond shape (classic flowchart)
- Dual output ports (true/false)
- Condition editor
- AI evaluation preview

#### 7. Template Selector Node
```typescript
{
  type: 'template-node',
  props: {
    platform: 'linkedin' | 'twitter' | 'instagram' | 'email',
    templateId: string,
    variables: Record<string, string>,
    preview: string,
  }
}
```

**Visual Design:**
- Platform icon + template name
- Variable editor
- Template preview modal
- Quick search

---

## Tier 2: AI Interpretation System

### Canvas Analysis Pipeline

```
User Clicks "Run Workflow" or "Interpret Canvas"
           ↓
┌──────────────────────────────────────────────────┐
│ 1. EXTRACT CANVAS STATE                          │
│    - Get all shapes (nodes, arrows, text, etc.)  │
│    - Get spatial relationships                   │
│    - Get text content from all elements          │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 2. BUILD CANVAS GRAPH                            │
│    - Identify connected components               │
│    - Detect flow direction (arrows)              │
│    - Group related elements                      │
│    - Extract hierarchy/sequence                  │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 3. LLM INTERPRETATION (Claude Code)              │
│    Input: Canvas JSON + spatial data             │
│    Prompt: "Analyze this canvas workflow and     │
│            convert it to executable steps"       │
│    Output: Structured workflow definition        │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 4. SKILL MAPPING                                 │
│    - Map interpreted steps → available skills    │
│    - "Find AI founders" → discovery-engine       │
│    - "Send LinkedIn message" → linkedin-adapter  │
│    - "Upload image" → attachment handler         │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 5. WORKFLOW GENERATION                           │
│    - Create workflow JSON                        │
│    - Add rate limiting rules                     │
│    - Insert delays between steps                 │
│    - Add error handling                          │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 6. USER APPROVAL                                 │
│    - Show interpreted workflow                   │
│    - Explain what will be executed               │
│    - Request confirmation                        │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ 7. EXECUTION                                     │
│    - Run via workflow-engine skill               │
│    - Real-time progress updates to canvas        │
│    - Highlight currently executing node          │
└──────────────────────────────────────────────────┘
```

### Canvas Interpretation Prompt Template

```typescript
const CANVAS_INTERPRETATION_PROMPT = `
You are analyzing a visual workflow canvas to convert it into an executable workflow.

CANVAS ELEMENTS:
{canvasJSON}

SPATIAL RELATIONSHIPS:
{connections}

TEXT CONTENT:
{allTextContent}

IMAGES/VIDEOS:
{mediaDescriptions}

TASK:
1. Understand the user's intent from the canvas layout
2. Identify the workflow sequence (what happens first, second, etc.)
3. Map each element to an available skill:
   - discovery-engine: Finding people/companies
   - linkedin-adapter: LinkedIn actions (connect, message, like, comment)
   - twitter-adapter: Twitter actions (follow, DM, like, retweet)
   - instagram-adapter: Instagram actions (follow, DM, like, comment)
   - gmail-adapter: Email sending
   - workflow-engine: Multi-step orchestration

4. Generate a structured workflow JSON with:
   - Step-by-step execution plan
   - Skill assignments
   - Parameters for each skill
   - Delays and rate limiting
   - Error handling

OUTPUT FORMAT:
{
  "workflowName": "User's Intent Title",
  "interpretation": "Your understanding of what the user wants",
  "steps": [
    {
      "stepNumber": 1,
      "canvasElement": "Rectangle labeled 'Find AI founders'",
      "interpretation": "Use discovery to find AI startup founders",
      "skill": "discovery-engine",
      "parameters": {
        "query": "AI startup founders",
        "maxResults": 50
      },
      "delayAfter": "none"
    },
    // ... more steps
  ],
  "estimatedDuration": "3-5 days",
  "touchPoints": 8,
  "platforms": ["linkedin", "email"]
}
`;
```

### Intelligent Shape Recognition

```typescript
// Shape Recognition Logic
function analyzeCanvasElement(shape: TLShape): ElementInterpretation {
  // Detect intent based on shape type, text, position

  if (shape.type === 'text' || shape.type === 'sticky-note') {
    const text = shape.props.text.toLowerCase();

    // Pattern matching for common intents
    if (text.includes('find') || text.includes('search') || text.includes('discover')) {
      return {
        intent: 'discovery',
        suggestedSkill: 'discovery-engine',
        confidence: 0.9,
        parameters: extractQueryFromText(text),
      };
    }

    if (text.includes('linkedin') && (text.includes('connect') || text.includes('message'))) {
      return {
        intent: 'linkedin_outreach',
        suggestedSkill: 'linkedin-adapter',
        confidence: 0.95,
        parameters: extractLinkedInAction(text),
      };
    }

    // ... more patterns
  }

  if (shape.type === 'arrow') {
    return {
      intent: 'sequence',
      suggestedSkill: null,
      confidence: 1.0,
      parameters: { direction: 'forward' },
    };
  }

  if (shape.type === 'diamond' || text.includes('if') || text.includes('?')) {
    return {
      intent: 'decision',
      suggestedSkill: 'conditional_logic',
      confidence: 0.85,
      parameters: extractCondition(text),
    };
  }

  // Fallback to LLM interpretation
  return {
    intent: 'unknown',
    suggestedSkill: 'llm_interpret',
    confidence: 0.5,
    parameters: { rawText: shape.props.text },
  };
}
```

---

## Tier 3: Enhanced Skill Execution

### Workflow Execution with Real-Time Canvas Updates

```typescript
// Execute workflow and update canvas in real-time
async function executeWorkflow(workflow: InterpretedWorkflow, editor: Editor) {
  for (const step of workflow.steps) {
    // Highlight currently executing node on canvas
    const canvasNode = findCanvasNodeForStep(step);
    if (canvasNode) {
      highlightNode(editor, canvasNode.id, 'running');
    }

    // Execute the skill
    try {
      const result = await executeSkill(step.skill, step.parameters);

      // Update canvas node status
      if (canvasNode) {
        updateNodeStatus(editor, canvasNode.id, 'completed', result);
      }

      // Wait for delay
      if (step.delayAfter) {
        await sleep(parseDelay(step.delayAfter));
      }

    } catch (error) {
      // Mark node as error
      if (canvasNode) {
        updateNodeStatus(editor, canvasNode.id, 'error', error.message);
      }
      throw error;
    }
  }
}

// Real-time node highlighting
function highlightNode(editor: Editor, nodeId: string, status: 'running' | 'completed' | 'error') {
  editor.updateShape({
    id: nodeId,
    type: 'skill-node',
    props: {
      status: status,
      // Running nodes pulse and animate
      // Completed nodes show checkmark
      // Error nodes show red border
    }
  });
}
```

---

## WebSocket Architecture (Bidirectional)

### Current System (HTTP Polling) ❌
- Client polls `/api/canvas/commands` every 500ms
- Inefficient, high latency
- Only one-way: Claude Code → Canvas

### New System (WebSocket) ✅

```
┌─────────────────────────┐          ┌─────────────────────────┐
│   Canvas Web App        │◄────────►│  WebSocket Server       │
│   (React + TLDraw)      │  Socket  │  (Node.js/Python)       │
└─────────────────────────┘          └──────────┬──────────────┘
                                                 │
                                                 │
                                      ┌──────────▼──────────────┐
                                      │   Claude Code           │
                                      │   (Skills + AI)         │
                                      └─────────────────────────┘

MESSAGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canvas → Server:
- canvas_updated: { shapes, timestamp }
- request_interpretation: { canvasState }
- workflow_executed: { workflowId }
- user_action: { type, data }

Server → Canvas:
- add_node: { id, type, x, y, props }
- update_node: { id, props }
- highlight_node: { id, status }
- add_connection: { from, to }
- show_notification: { message, type }
- workflow_progress: { step, status }

Server → Claude Code:
- canvas_changed: { shapes, interpretation_needed }
- workflow_ready: { workflowJSON }

Claude Code → Server:
- execute_workflow: { steps }
- update_node_status: { nodeId, status }
- send_notification: { message }
```

### WebSocket Server Implementation

```typescript
// canvas/server/websocket-server.ts
import WebSocket from 'ws';
import express from 'express';
import { Server } from 'http';

const app = express();
const server = new Server(app);
const wss = new WebSocket.Server({ server });

// Connected clients
const clients = new Map<string, WebSocket>();
let claudeCodeClient: WebSocket | null = null;

wss.on('connection', (ws: WebSocket, req) => {
  const clientType = req.headers['x-client-type'];

  if (clientType === 'canvas') {
    const clientId = generateId();
    clients.set(clientId, ws);
    console.log(`Canvas client connected: ${clientId}`);

    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      handleCanvasMessage(message, clientId);
    });

  } else if (clientType === 'claude-code') {
    claudeCodeClient = ws;
    console.log('Claude Code connected');

    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      handleClaudeCodeMessage(message);
    });
  }

  ws.on('close', () => {
    if (clientType === 'canvas') {
      clients.delete(clientId);
    } else {
      claudeCodeClient = null;
    }
  });
});

// Handle messages from Canvas
function handleCanvasMessage(message: any, clientId: string) {
  switch (message.type) {
    case 'canvas_updated':
      // Forward to Claude Code for potential interpretation
      if (claudeCodeClient) {
        claudeCodeClient.send(JSON.stringify({
          type: 'canvas_changed',
          data: message.data,
        }));
      }
      break;

    case 'request_interpretation':
      // User clicked "Interpret Canvas" button
      if (claudeCodeClient) {
        claudeCodeClient.send(JSON.stringify({
          type: 'interpret_canvas',
          data: message.data,
        }));
      }
      break;

    case 'workflow_executed':
      // User clicked "Run" button
      if (claudeCodeClient) {
        claudeCodeClient.send(JSON.stringify({
          type: 'run_workflow',
          data: message.data,
        }));
      }
      break;
  }
}

// Handle messages from Claude Code
function handleClaudeCodeMessage(message: any) {
  // Broadcast to all canvas clients
  const payload = JSON.stringify(message);
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(payload);
    }
  });
}

server.listen(3001, () => {
  console.log('WebSocket server running on ws://localhost:3001');
});
```

### Canvas Client Integration

```typescript
// canvas/src/hooks/useWebSocket.ts
import { useEffect, useRef } from 'react';
import { Editor } from 'tldraw';

export function useWebSocket(editor: Editor | null) {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!editor) return;

    // Connect to WebSocket server
    const ws = new WebSocket('ws://localhost:3001');
    ws.onopen = () => {
      console.log('WebSocket connected');
      // Identify as canvas client
      ws.send(JSON.stringify({
        type: 'identify',
        clientType: 'canvas',
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message, editor);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    wsRef.current = ws;

    // Listen to canvas changes
    const unsubscribe = editor.store.listen((entry) => {
      if (entry.source === 'user') {
        // Debounce and send canvas state
        sendCanvasUpdate(ws, editor);
      }
    });

    return () => {
      ws.close();
      unsubscribe();
    };
  }, [editor]);

  return wsRef;
}

function handleMessage(message: any, editor: Editor) {
  switch (message.type) {
    case 'add_node':
      editor.createShape({
        id: message.data.id,
        type: message.data.type,
        x: message.data.x,
        y: message.data.y,
        props: message.data.props,
      });
      break;

    case 'update_node':
      editor.updateShape({
        id: message.data.id,
        type: message.data.type,
        props: message.data.props,
      });
      break;

    case 'highlight_node':
      // Highlight with animation
      highlightNode(editor, message.data.id, message.data.status);
      break;

    case 'workflow_progress':
      // Show progress notification
      showNotification(message.data.message, message.data.type);
      break;
  }
}
```

---

## Implementation Roadmap

### Phase 1: Enhanced Canvas (Week 1-2)
**Goal**: Add new node types and freeform drawing

- [ ] Create PromptNodeShapeUtil
- [ ] Create ImageNodeShapeUtil with drag-drop upload
- [ ] Create VideoNodeShapeUtil with upload
- [ ] Create FreeformTextNodeShapeUtil with markdown
- [ ] Create DrawingNodeShapeUtil for freehand
- [ ] Create DecisionNodeShapeUtil (diamond shape)
- [ ] Update WorkflowSidebar to show new node types
- [ ] Add file upload API endpoints
- [ ] Test all new nodes on canvas

**Deliverables:**
- 6 new custom shapes
- File upload system
- Enhanced sidebar UI

### Phase 2: WebSocket Infrastructure (Week 2-3)
**Goal**: Replace HTTP polling with bidirectional WebSocket

- [ ] Create canvas/server/websocket-server.ts
- [ ] Implement client connection handling
- [ ] Implement message routing (Canvas ↔ Claude Code)
- [ ] Create useWebSocket hook for Canvas
- [ ] Create WebSocket client for Claude Code
- [ ] Migrate existing commands to WebSocket messages
- [ ] Add reconnection logic
- [ ] Add heartbeat/ping-pong
- [ ] Test bidirectional communication

**Deliverables:**
- WebSocket server (Node.js)
- Canvas WebSocket client
- Claude Code WebSocket client
- Real-time updates working

### Phase 3: AI Interpretation Layer (Week 3-5)
**Goal**: Build the magic - canvas understanding and workflow generation

- [ ] Create canvas-analyzer.ts (extract shapes, text, connections)
- [ ] Create graph-builder.ts (build workflow graph from canvas)
- [ ] Create llm-interpreter.ts (Claude API integration)
- [ ] Design canvas interpretation prompts
- [ ] Implement skill mapping logic
- [ ] Create workflow generator from interpreted canvas
- [ ] Add confidence scoring
- [ ] Build user approval UI
- [ ] Test with various canvas configurations

**Deliverables:**
- Canvas analysis engine
- LLM interpretation system
- Workflow generation pipeline
- Approval UI

### Phase 4: Enhanced Execution (Week 5-6)
**Goal**: Execute interpreted workflows with real-time visual feedback

- [ ] Create workflow executor with canvas updates
- [ ] Implement node highlighting during execution
- [ ] Add progress indicators
- [ ] Add error visualization
- [ ] Create execution logs panel
- [ ] Add pause/resume capability
- [ ] Add cancel workflow feature
- [ ] Test end-to-end workflow execution

**Deliverables:**
- Real-time execution engine
- Visual feedback system
- Execution controls

### Phase 5: Advanced Features (Week 6-8)
**Goal**: Polish and advanced capabilities

- [ ] Add vision API for image analysis
- [ ] Add video transcription for video nodes
- [ ] Implement collaborative editing (multi-user)
- [ ] Add canvas templates library
- [ ] Add workflow versioning
- [ ] Add A/B testing for workflows
- [ ] Add analytics dashboard
- [ ] Comprehensive testing

**Deliverables:**
- Vision + Video AI
- Collaboration features
- Template library
- Analytics

---

## Example User Flows

### Flow 1: Sketch-to-Workflow

**User Actions:**
1. Opens canvas
2. Draws a rectangle, types "Find AI startup founders in San Francisco"
3. Draws arrow →
4. Draws another rectangle, types "Check their LinkedIn profiles"
5. Draws arrow →
6. Adds text box: "Send personalized message about our product"
7. Clicks "Interpret Canvas"

**System Response:**
1. Analyzes canvas shapes and text
2. Claude Code interprets:
   - Step 1 → discovery-engine (query: "AI startup founders San Francisco")
   - Step 2 → linkedin-adapter (action: view_profile)
   - Step 3 → linkedin-adapter (action: message, template: personalized)
3. Shows approval dialog:
   ```
   INTERPRETED WORKFLOW

   1. Discovery: Find AI startup founders in San Francisco (max 50)
   2. LinkedIn: View each profile (warm-up)
   3. Wait 24 hours
   4. LinkedIn: Send personalized connection request
   5. Wait 48 hours
   6. LinkedIn: Send introduction message

   Estimated duration: 5-7 days
   Total touches: 3 per person

   [Approve] [Edit] [Cancel]
   ```
4. User clicks Approve
5. Workflow executes with real-time canvas highlighting

### Flow 2: Image + Prompt Workflow

**User Actions:**
1. Drags product screenshot onto canvas
2. Adds description: "Our new AI coding assistant"
3. Draws arrow from image →
4. Adds prompt node: "Show this to developers on Twitter who tweet about AI"
5. Draws arrow →
6. Adds text: "Send DM asking if they want early access"
7. Clicks "Run Workflow"

**System Response:**
1. Vision API analyzes image
2. Claude Code interprets:
   - Use image as reference
   - discovery-engine: Find developers tweeting about AI
   - twitter-adapter: Show them the product (like their tweets)
   - twitter-adapter: Send DM with image + message
3. Executes workflow with rate limiting

### Flow 3: Complex Multi-Platform

**User Actions:**
1. Sticky note: "Target: SaaS founders"
2. Arrow → Rectangle: "Find on LinkedIn"
3. Arrow → Decision diamond: "Do they have Twitter?"
4. True arrow → "Follow on Twitter"
5. False arrow → "Send LinkedIn connection"
6. Both merge → "Wait 3 days"
7. Arrow → "Send email pitch"
8. Uploads pitch deck PDF
9. Clicks "Interpret & Run"

**System Response:**
1. Understands conditional logic (if-then-else)
2. Maps to workflow with branching:
   - discovery-engine
   - Conditional: check for Twitter handle
   - Branch A: twitter-adapter (follow)
   - Branch B: linkedin-adapter (connect)
   - Merge: delay 3 days
   - gmail-adapter (send email with attachment)
3. Executes with intelligent branching per target

---

## Technical Specifications

### File Upload System

```typescript
// canvas/server/upload.ts
import multer from 'multer';
import path from 'path';
import crypto from 'crypto';

const storage = multer.diskStorage({
  destination: './uploads/',
  filename: (req, file, cb) => {
    const hash = crypto.randomBytes(16).toString('hex');
    cb(null, `${hash}${path.extname(file.originalname)}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB
  },
  fileFilter: (req, file, cb) => {
    const allowed = /jpeg|jpg|png|gif|mp4|mov|avi|pdf/;
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowed.test(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

app.post('/api/upload', upload.single('file'), (req, res) => {
  const file = req.file;
  if (!file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  res.json({
    fileId: file.filename,
    url: `/uploads/${file.filename}`,
    type: file.mimetype,
    size: file.size,
  });
});
```

### Vision API Integration

```typescript
// .claude/scripts/vision_analyzer.py
import anthropic
import base64

def analyze_image(image_path: str, question: str = "What's in this image?"):
    client = anthropic.Anthropic()

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": question
                }
            ],
        }],
    )

    return response.content[0].text
```

---

## Success Metrics

### User Experience
- **Canvas Flexibility**: Users can draw ANY workflow shape
- **Interpretation Accuracy**: 90%+ correct skill mapping
- **Time to Workflow**: < 5 minutes from idea to execution
- **Learning Curve**: New users productive in < 10 minutes

### Technical Performance
- **WebSocket Latency**: < 100ms for node updates
- **Canvas Load Time**: < 2s for 100+ nodes
- **Interpretation Time**: < 5s for complex canvas
- **Upload Speed**: 10MB image in < 3s

### Business Impact
- **Workflow Creation**: 10x faster than manual coding
- **Error Rate**: < 5% failed workflows
- **User Adoption**: 80%+ prefer canvas over CLI
- **Automation**: 50+ steps automated per workflow

---

## Risk Mitigation

### Technical Risks

**Risk**: LLM misinterprets canvas
**Mitigation**:
- Always show interpretation before execution
- Confidence scoring (reject < 70%)
- Allow manual correction
- Learn from corrections

**Risk**: WebSocket connection drops
**Mitigation**:
- Auto-reconnect with exponential backoff
- Queue messages during disconnect
- Fallback to HTTP polling
- Show connection status indicator

**Risk**: Large file uploads fail
**Mitigation**:
- Chunked upload with resumability
- Progress indicators
- File size limits
- Format validation

### User Experience Risks

**Risk**: Too much complexity confuses users
**Mitigation**:
- Simple onboarding tutorial
- Template library
- Tooltips and hints
- Progressive disclosure

**Risk**: Workflow interpretation is opaque
**Mitigation**:
- Show detailed interpretation before execution
- Explain each mapped skill
- Allow step-by-step review
- Provide edit capability

---

## Conclusion

This design transforms the 10x-Team Canvas from a **predefined node builder** into a **revolutionary AI-powered freeform canvas** where:

✅ Users can **draw anything** (rectangles, arrows, text, sketches)
✅ Users can **upload media** (images, videos) with descriptions
✅ Users can **write prompts** in natural language
✅ **Claude Code interprets** the canvas using AI
✅ **Workflows are generated automatically** from drawings
✅ **Execution happens in real-time** with visual feedback
✅ **WebSocket enables bidirectional** Canvas ↔ Claude Code communication

**The bigger idea is realized**: Draw anything and Claude Code will do it.

---

## Next Steps

1. **Review this design document**
2. **Approve architecture decisions**
3. **Begin Phase 1 implementation** (Enhanced Canvas)
4. **Set up development environment**
5. **Create implementation tickets**

---

**Document Version**: 1.0
**Last Updated**: 2026-01-22
**Author**: Claude Code (Sonnet 4.5)
**Status**: Awaiting User Approval

---

## Appendix: Research Sources

### TLDraw Official Documentation
- [TLDraw SDK](https://tldraw.dev/)
- [Custom Shapes](https://tldraw.dev/examples/custom-shape)
- [Editor API](https://tldraw.dev/docs/editor)
- [Bindings System](https://tldraw.dev/reference/tlschema/TLArrowBindingProps)

### Node-Based UI Patterns
- [n8n Node UI Design](https://docs.n8n.io/integrations/creating-nodes/plan/node-ui-design/)
- [React Flow](https://reactflow.dev)
- [Flume](https://flume.dev/)
- [Rete.js](https://retejs.org/)

### AI Canvas Interpretation
- [Jeda.ai Visual AI Flowcharts](https://www.jeda.ai/visual-ai-flowcharts-diagrams)
- [Canvas by Thesys AI Workflows](https://medium.com/@ShawnBasquiat/ai-agent-workflows-in-minutes-86d06897b314)
- [Lucidchart AI Diagrams](https://www.lucidchart.com/pages/use-cases/diagram-with-AI)

### LLM Orchestration
- [LLM Orchestration 2026](https://orq.ai/blog/llm-orchestration)
- [WorkflowLLM](https://arxiv.org/html/2411.05451v1)
- [Prompt Orchestration](https://blog.promptlayer.com/prompt-orchestration/)

### WebSocket Real-Time
- [React + Socket.io Whiteboard](https://geextor.com/2025/08/22/build-real-time-collaborative-whiteboard-with-react-socket-io/)
- [WebSocket Tutorial React](https://blog.logrocket.com/websocket-tutorial-real-time-node-react/)

### Drag-Drop React Libraries
- [Top 5 Drag-Drop Libraries 2026](https://puckeditor.com/blog/top-5-drag-and-drop-libraries-for-react)
- [React Flow Drag and Drop](https://reactflow.dev/examples/interaction/drag-and-drop)

---

*This design document represents the comprehensive research and architectural planning for the revolutionary "Draw Anything and Claude Code Will Do It" system.*
