import express from 'express';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import { createServer } from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Create HTTP server
const server = createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server, path: '/ws' });

// Store commands queue (for backwards compatibility)
const commandsQueue = [];
let commandIdCounter = 0;

// Track connected clients
const clients = new Set();

// WebSocket connection handler
wss.on('connection', (ws) => {
  console.log('✅ Canvas client connected via WebSocket');
  clients.add(ws);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to 10x-Team Canvas Server',
    timestamp: Date.now()
  }));

  ws.on('close', () => {
    console.log('❌ Canvas client disconnected');
    clients.delete(ws);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    clients.delete(ws);
  });
});

// Broadcast to all connected clients
function broadcast(data) {
  const message = JSON.stringify(data);
  clients.forEach((client) => {
    if (client.readyState === 1) { // 1 = OPEN
      client.send(message);
    }
  });
}

// API: Send command to canvas (from Claude Code)
app.post('/api/canvas/command', (req, res) => {
  const command = {
    id: `cmd-${++commandIdCounter}-${Date.now()}`,
    timestamp: Date.now(),
    ...req.body
  };

  console.log('📤 Received command from Claude Code:', command.type);

  // Add to queue (for polling fallback)
  commandsQueue.push(command);
  if (commandsQueue.length > 100) {
    commandsQueue.shift(); // Keep only last 100 commands
  }

  // Broadcast via WebSocket
  broadcast(command);

  res.json({
    success: true,
    commandId: command.id,
    clients: clients.size,
    broadcast: clients.size > 0
  });
});

// API: Batch commands (for sequential operations)
app.post('/api/canvas/commands/batch', (req, res) => {
  const { commands: incomingCommands } = req.body;

  if (!Array.isArray(incomingCommands)) {
    return res.status(400).json({ error: 'Commands must be an array' });
  }

  const processedCommands = incomingCommands.map(cmd => ({
    id: `cmd-${++commandIdCounter}-${Date.now()}`,
    timestamp: Date.now(),
    ...cmd
  }));

  console.log(`📤 Received ${processedCommands.length} batch commands from Claude Code`);

  // Add to queue
  commandsQueue.push(...processedCommands);
  while (commandsQueue.length > 100) {
    commandsQueue.shift();
  }

  // Broadcast all commands
  processedCommands.forEach(command => {
    broadcast(command);
  });

  res.json({
    success: true,
    commandCount: processedCommands.length,
    clients: clients.size
  });
});

// API: Poll for commands (backwards compatibility)
app.get('/api/canvas/commands', (req, res) => {
  const { lastId } = req.query;

  let commands = commandsQueue;

  // Filter commands after lastId
  if (lastId) {
    const lastIndex = commands.findIndex(cmd => cmd.id === lastId);
    if (lastIndex >= 0) {
      commands = commands.slice(lastIndex + 1);
    }
  }

  res.json({
    commands,
    total: commandsQueue.length
  });
});

// API: Clear all commands
app.post('/api/canvas/clear', (req, res) => {
  commandsQueue.length = 0;
  broadcast({ type: 'clear', timestamp: Date.now() });
  res.json({ success: true });
});

// API: Get server status
app.get('/api/status', (req, res) => {
  res.json({
    status: 'running',
    clients: clients.size,
    commandsQueued: commandsQueue.length,
    uptime: process.uptime(),
    timestamp: Date.now()
  });
});

// API: Save workflow (from canvas)
app.post('/api/workflow/save', (req, res) => {
  const { workflow, name, description } = req.body;

  if (!workflow) {
    return res.status(400).json({ error: 'Workflow data is required' });
  }

  // Generate contextual workflow name
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  let workflowName = name;

  if (!workflowName) {
    // Extract context from workflow
    const nodeCount = workflow.nodes?.length || 0;
    const platforms = new Set();

    // Identify platforms used
    workflow.nodes?.forEach(node => {
      if (node.skillType) {
        platforms.add(node.skillType);
      }
    });

    const platformList = Array.from(platforms).slice(0, 3).join('-');
    const platformStr = platformList || 'workflow';

    // Create descriptive name: platform-nodes-timestamp
    workflowName = `${platformStr}-${nodeCount}nodes-${timestamp}`;
  }

  // Ensure output directory exists
  const outputDir = path.join(__dirname, '..', 'output', 'workflows');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Enhanced workflow object with metadata
  const workflowWithMeta = {
    ...workflow,
    metadata: {
      name: workflowName,
      description: description || `Workflow with ${workflow.nodes?.length || 0} nodes`,
      created: new Date().toISOString(),
      nodeCount: workflow.nodes?.length || 0,
      platforms: workflow.nodes?.map(n => n.skillType).filter(Boolean) || [],
      status: 'pending', // pending, running, completed, failed
      executed: false,
      executionHistory: []
    }
  };

  // Save workflow with timestamp and context
  const workflowPath = path.join(outputDir, `${workflowName}.json`);
  fs.writeFileSync(workflowPath, JSON.stringify(workflowWithMeta, null, 2));

  // Save as latest.json with full metadata
  const latestPath = path.join(outputDir, 'latest.json');
  fs.writeFileSync(latestPath, JSON.stringify(workflowWithMeta, null, 2));

  // Save to project root as workflow.json (quick access)
  const rootPath = path.join(__dirname, '..', 'workflow.json');
  fs.writeFileSync(rootPath, JSON.stringify(workflowWithMeta, null, 2));

  // Update workflow index (for easy listing)
  const indexPath = path.join(outputDir, 'index.json');
  let index = { workflows: [] };

  if (fs.existsSync(indexPath)) {
    try {
      index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    } catch (e) {
      console.error('Failed to read workflow index:', e);
    }
  }

  // Add to index
  index.workflows = index.workflows || [];
  index.workflows.push({
    name: workflowName,
    path: workflowPath,
    created: workflowWithMeta.metadata.created,
    nodeCount: workflowWithMeta.metadata.nodeCount,
    platforms: workflowWithMeta.metadata.platforms,
    status: 'pending',
    description: workflowWithMeta.metadata.description
  });

  // Keep only last 100 workflows in index
  if (index.workflows.length > 100) {
    index.workflows = index.workflows.slice(-100);
  }

  fs.writeFileSync(indexPath, JSON.stringify(index, null, 2));

  console.log(`💾 Workflow saved: ${workflowName} (${workflowWithMeta.metadata.nodeCount} nodes)`);

  res.json({
    success: true,
    path: workflowPath,
    name: workflowName,
    metadata: workflowWithMeta.metadata
  });
});

// API: Process video URL (YouTube, LinkedIn, etc.)
app.post('/api/video/process', async (req, res) => {
  const { nodeId, url, videoPath } = req.body;

  if (!nodeId || (!url && !videoPath)) {
    return res.status(400).json({ error: 'nodeId and url or videoPath required' });
  }

  console.log(`🎥 Processing video request: ${url || videoPath}`);

  try {
    // Spawn Python video processor
    const { spawn } = await import('child_process');
    const { platform } = await import('os');

    // Determine Python executable path (use venv if available)
    const venvPath = path.join(__dirname, '..', '.venv');
    let pythonCmd = 'python';

    if (fs.existsSync(venvPath)) {
      if (platform() === 'win32') {
        pythonCmd = path.join(venvPath, 'Scripts', 'python.exe');
      } else {
        pythonCmd = path.join(venvPath, 'bin', 'python');
      }
      console.log('🐍 Using virtual environment Python:', pythonCmd);
    }

    const pythonPath = path.join(__dirname, '..', '.claude', 'scripts', 'video_processor.py');

    const args = url
      ? ['url', url]
      : ['process', videoPath];

    const process = spawn(pythonCmd, [pythonPath, ...args]);

    let output = '';
    let error = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`Video processor: ${data}`);

      // Broadcast progress updates
      broadcast({
        type: 'video-processing-progress',
        nodeId,
        message: data.toString()
      });
    });

    process.stderr.on('data', (data) => {
      error += data.toString();
      console.error(`Video processor error: ${data}`);
    });

    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);

          // Broadcast completion
          broadcast({
            type: 'video-processing-complete',
            nodeId,
            result
          });

          res.json({ success: true, result });
        } catch (e) {
          res.json({ success: true, output });
        }
      } else {
        broadcast({
          type: 'video-processing-error',
          nodeId,
          error: error || 'Processing failed'
        });
        res.status(500).json({ error: error || 'Processing failed' });
      }
    });

  } catch (err) {
    console.error('Video processing error:', err);
    res.status(500).json({ error: err.message });
  }
});

// API: List workflows
app.get('/api/workflows', (req, res) => {
  const outputDir = path.join(__dirname, '..', 'output', 'workflows');
  const indexPath = path.join(outputDir, 'index.json');

  if (!fs.existsSync(indexPath)) {
    return res.json({ workflows: [] });
  }

  try {
    const index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

    // Sort by created date (newest first)
    index.workflows.sort((a, b) => new Date(b.created) - new Date(a.created));

    res.json(index);
  } catch (error) {
    console.error('Failed to read workflow index:', error);
    res.status(500).json({ error: 'Failed to read workflows' });
  }
});

// API: Get workflow by name
app.get('/api/workflow/:name', (req, res) => {
  const { name } = req.params;
  const outputDir = path.join(__dirname, '..', 'output', 'workflows');
  const workflowPath = path.join(outputDir, `${name}.json`);

  if (!fs.existsSync(workflowPath)) {
    return res.status(404).json({ error: 'Workflow not found' });
  }

  try {
    const workflow = JSON.parse(fs.readFileSync(workflowPath, 'utf-8'));
    res.json(workflow);
  } catch (error) {
    console.error('Failed to read workflow:', error);
    res.status(500).json({ error: 'Failed to read workflow' });
  }
});

// API: Update workflow status
app.post('/api/workflow/:name/status', (req, res) => {
  const { name } = req.params;
  const { status, executed, executionResult } = req.body;

  const outputDir = path.join(__dirname, '..', 'output', 'workflows');
  const workflowPath = path.join(outputDir, `${name}.json`);
  const indexPath = path.join(outputDir, 'index.json');

  if (!fs.existsSync(workflowPath)) {
    return res.status(404).json({ error: 'Workflow not found' });
  }

  try {
    // Update workflow file
    const workflow = JSON.parse(fs.readFileSync(workflowPath, 'utf-8'));

    if (!workflow.metadata) {
      workflow.metadata = {};
    }

    if (status) workflow.metadata.status = status;
    if (executed !== undefined) workflow.metadata.executed = executed;

    if (executionResult) {
      workflow.metadata.executionHistory = workflow.metadata.executionHistory || [];
      workflow.metadata.executionHistory.push({
        timestamp: new Date().toISOString(),
        status: status,
        result: executionResult
      });
    }

    workflow.metadata.lastUpdated = new Date().toISOString();

    fs.writeFileSync(workflowPath, JSON.stringify(workflow, null, 2));

    // Update index
    if (fs.existsSync(indexPath)) {
      const index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
      const workflowEntry = index.workflows.find(w => w.name === name);

      if (workflowEntry) {
        if (status) workflowEntry.status = status;
        if (executed !== undefined) workflowEntry.executed = executed;
        workflowEntry.lastUpdated = workflow.metadata.lastUpdated;
      }

      fs.writeFileSync(indexPath, JSON.stringify(index, null, 2));
    }

    console.log(`📝 Workflow status updated: ${name} → ${status}`);

    res.json({
      success: true,
      workflow: workflow.metadata
    });
  } catch (error) {
    console.error('Failed to update workflow:', error);
    res.status(500).json({ error: 'Failed to update workflow' });
  }
});

// API: Get latest workflow
app.get('/api/workflow/latest', (req, res) => {
  const latestPath = path.join(__dirname, '..', 'output', 'workflows', 'latest.json');

  if (!fs.existsSync(latestPath)) {
    return res.status(404).json({ error: 'No workflows found' });
  }

  try {
    const workflow = JSON.parse(fs.readFileSync(latestPath, 'utf-8'));
    res.json(workflow);
  } catch (error) {
    console.error('Failed to read latest workflow:', error);
    res.status(500).json({ error: 'Failed to read workflow' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Start server
server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║        10x-Team Canvas WebSocket Server Started              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  HTTP Server:    http://localhost:${PORT}                       ║
║  WebSocket:      ws://localhost:${PORT}/ws                      ║
║                                                              ║
║  Canvas Commands (WebSocket):                                ║
║  POST /api/canvas/command        - Send single command      ║
║  POST /api/canvas/commands/batch - Send batch commands      ║
║  GET  /api/canvas/commands       - Poll commands (legacy)   ║
║  POST /api/canvas/clear          - Clear canvas             ║
║                                                              ║
║  Workflow Management:                                        ║
║  POST /api/workflow/save         - Save workflow            ║
║  GET  /api/workflows             - List all workflows       ║
║  GET  /api/workflow/latest       - Get latest workflow      ║
║  GET  /api/workflow/:name        - Get workflow by name     ║
║  POST /api/workflow/:name/status - Update workflow status   ║
║                                                              ║
║  System:                                                     ║
║  GET  /api/status                - Server status            ║
║  GET  /health                    - Health check             ║
║                                                              ║
║  Features:                                                   ║
║  ✅ WebSocket real-time updates                              ║
║  ✅ Virtual environment Python support                       ║
║  ✅ Contextual workflow naming                               ║
║  ✅ Workflow execution tracking                              ║
║  ✅ n8n-style connection deletion                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);
});
