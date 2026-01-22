# TLDraw Canvas - Standalone Application

A clean, portable TLDraw canvas implementation using the **official TLDraw SDK**.

**Developed by 10x.in**

## About This Application

This is a **standalone, portable** TLDraw implementation that can be easily copied to any skill or project. It uses the official TLDraw SDK with zero custom modifications - providing the pure TLDraw experience as documented at [tldraw.dev](https://tldraw.dev).

## Features

All features are provided by the official TLDraw SDK:

- ✨ **Infinite Canvas** - Pan and zoom freely across unlimited space
- 🎨 **Drawing Tools** - Pen, highlighter, eraser
- 📐 **Shapes** - Rectangle, ellipse, arrow, line, text, and more
- 🖼️ **Media** - Embed images and videos
- 📋 **Copy/Paste** - Full clipboard support with fidelity
- ↩️ **Undo/Redo** - Complete history tracking
- 💾 **Export** - PNG, SVG, or JSON format
- 🔄 **Auto-Save** - Automatic persistence to localStorage
- 👥 **Multiplayer** - Real-time collaboration (optional)

## Quick Start

### Installation

```bash
cd tldraw-canvas
npm install
```

### Development

```bash
npm run dev
```

Opens at **http://localhost:3000**

### Production Build

```bash
npm run build
```

## How to Use

1. **Start the canvas** - Run `npm run dev`
2. **Draw & Create** - Use the toolbar to select tools and draw on the canvas
3. **Add Shapes** - Click shape buttons to add rectangles, ellipses, arrows, etc.
4. **Add Media** - Drag and drop images or videos onto the canvas
5. **Pan & Zoom** - Mouse drag to pan, scroll wheel to zoom
6. **Select & Transform** - Click to select shapes, drag handles to resize/rotate
7. **Copy/Paste** - Use Ctrl+C / Ctrl+V (Cmd+C / Cmd+V on Mac)
8. **Undo/Redo** - Ctrl+Z / Ctrl+Shift+Z (Cmd+Z / Cmd+Shift+Z on Mac)
9. **Export** - Use the menu to export as PNG, SVG, or JSON

## Project Structure

```
tldraw-canvas/
├── src/
│   ├── App.tsx           # Main TLDraw component
│   ├── main.tsx          # React entry point
│   └── index.css         # Global styles
├── package.json          # Dependencies (tldraw, react, vite)
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
├── index.html            # HTML template
└── README.md             # This file
```

## Copying to Other Skills

This folder is designed to be **easily portable**. To use in another skill:

1. **Copy the entire folder** to your target skill directory
2. **Run `npm install`** in the copied folder
3. **Update the port** in `vite.config.ts` if needed (default: 3000)
4. **Start with `npm run dev`**

That's it! No configuration needed.

## TLDraw SDK Resources

- **Official Docs**: https://tldraw.dev
- **Quick Start Guide**: https://tldraw.dev/quick-start
- **API Reference**: https://tldraw.dev/api
- **Examples**: https://tldraw.dev/examples
- **GitHub**: https://github.com/tldraw/tldraw

## Technical Details

- **TLDraw Version**: 4.3.0 (latest)
- **React Version**: 19.2.0
- **Build Tool**: Vite 7.2.4
- **Language**: TypeScript
- **License**: MIT

## Support

For TLDraw issues, refer to the [official documentation](https://tldraw.dev) or [GitHub repository](https://github.com/tldraw/tldraw).

For integration with 10x.in skills, contact: **Developed by 10x.in**

---

**Made with** [TLDraw](https://tldraw.dev) | **Developed by 10x.in**
