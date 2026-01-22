# Start App Command

When the user says "start my app", "start the app", "start canvas", or similar:

## Automatic Startup Sequence

Execute the following steps in order:

### 1. Check Dependencies
```bash
cd canvas && npm install
```

### 2. Build the App
```bash
cd canvas && npm run build
```

### 3. Start Development Server on Port 3000
```bash
cd canvas && npm run dev -- --port 3000
```

### 4. Notify User
After the server starts, inform the user:
- Canvas is running at http://localhost:3000
- Auto-save is enabled
- Drag green ▶ to blue ◀ to connect nodes
- Click Run to export workflow

## Quick Start (if already installed)
If node_modules exists, skip install and just run:
```bash
cd canvas && npm run dev -- --port 3000
```
