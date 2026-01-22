---
name: canvas
description: Open the 10x-Team visual workflow canvas
---

# /canvas Command

Opens the 10x-Team visual workflow canvas for designing outreach workflows.

## Usage

```
/canvas [action]
```

### Actions

- `/canvas` or `/canvas open` - Start the canvas server
- `/canvas build` - Build for production
- `/canvas stop` - Stop the canvas server

## Starting the Canvas

```bash
cd canvas && npm run dev -- --port 3006
```

Then open: **http://localhost:3006/**

## What You Can Do

1. **Add Nodes** - Click skill icons in the toolbar
2. **Load Templates** - Pre-built workflow configurations
3. **Design Workflows** - Drag and arrange nodes
4. **Export** - Copy workflow JSON for execution
5. **Execute** - Use Claude Code to run the workflow

## Workflow Templates

- 💼 **B2B Outreach** - LinkedIn + Email sequence
- 🤝 **Brand Partnership** - Instagram + Twitter + Email
- ⭐ **Influencer Outreach** - Social engagement + pitch
- 🌐 **Multi-Platform** - All channels adaptive

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Delete | Remove selected nodes |
| Ctrl+A | Select all |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Scroll | Zoom in/out |

## Integration

The canvas exports JSON that Claude Code can execute:

1. Design your workflow on canvas
2. Click "Export" to copy JSON
3. Tell Claude Code: "Run this workflow" + paste JSON
4. Claude Code orchestrates the execution
