# Start App Command

When the user says "start my app", "start the app", "start canvas", or similar:

## Automatic Startup Sequence

### 1. Check Dependencies
```bash
cd tldraw-canvas && npm install
```

### 2. Start Development Server on Port 3000
```bash
cd tldraw-canvas && npm run dev
```

### 3. Notify User
After the server starts, inform the user:
- Canvas is running at http://localhost:3000
- Official TLDraw SDK — infinite canvas with drawing, shapes, media, export
- Auto-save to localStorage is enabled

## Quick Start (if already installed)
If node_modules exists, skip install and just run:
```bash
cd tldraw-canvas && npm run dev
```
