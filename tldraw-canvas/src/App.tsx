import { Tldraw } from 'tldraw'
import 'tldraw/tldraw.css'

/**
 * TLDraw Canvas - Official SDK Implementation
 *
 * This is a clean, standalone implementation of TLDraw using the official SDK.
 * No custom modifications - pure TLDraw experience as documented at tldraw.dev
 *
 * Features (all provided by TLDraw SDK):
 * - Infinite canvas with pan and zoom
 * - Drawing tools (pen, highlighter, eraser)
 * - Shapes (rectangle, ellipse, arrow, line, text)
 * - Images and videos
 * - Copy/paste with full fidelity
 * - Undo/redo with complete history
 * - Export as PNG, SVG, or JSON
 * - Auto-save to localStorage
 * - Multiplayer support (optional)
 *
 * Developed by 10x.in
 * Learn more: https://tldraw.dev
 */

function App() {
  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <Tldraw />
    </div>
  )
}

export default App
