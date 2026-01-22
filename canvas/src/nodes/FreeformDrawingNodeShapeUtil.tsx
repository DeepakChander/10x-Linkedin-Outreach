import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'
import { useState, useRef, useEffect } from 'react'

// Freeform Drawing node for sketches and annotations
export type FreeformDrawingNodeShape = TLBaseShape<
  'freeform-drawing-node',
  {
    w: number
    h: number
    drawing: string // Data URL of the canvas drawing
    description: string
    backgroundColor: string
    brushColor: string
    brushSize: number
    tool: 'pen' | 'eraser' | 'highlighter'
    tags: string[]
  }
>

export class FreeformDrawingNodeShapeUtil extends BaseBoxShapeUtil<FreeformDrawingNodeShape> {
  static override type = 'freeform-drawing-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    drawing: T.string,
    description: T.string,
    backgroundColor: T.string,
    brushColor: T.string,
    brushSize: T.number,
    tool: T.string,
    tags: T.arrayOf(T.string),
  }

  getDefaultProps(): FreeformDrawingNodeShape['props'] {
    return {
      w: 400,
      h: 400,
      drawing: '',
      description: 'Freeform Drawing',
      backgroundColor: '#ffffff',
      brushColor: '#000000',
      brushSize: 3,
      tool: 'pen',
      tags: [],
    }
  }

  component(shape: FreeformDrawingNodeShape) {
    const [isDrawing, setIsDrawing] = useState(false)
    const [currentTool, setCurrentTool] = useState<'pen' | 'eraser' | 'highlighter'>(shape.props.tool)
    const [currentColor, setCurrentColor] = useState(shape.props.brushColor)
    const [currentSize, setCurrentSize] = useState(shape.props.brushSize)
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const editor = this.editor

    // Initialize canvas with saved drawing
    useEffect(() => {
      if (canvasRef.current && shape.props.drawing) {
        const ctx = canvasRef.current.getContext('2d')
        if (ctx) {
          const img = new Image()
          img.onload = () => {
            ctx.clearRect(0, 0, canvasRef.current!.width, canvasRef.current!.height)
            ctx.drawImage(img, 0, 0)
          }
          img.src = shape.props.drawing
        }
      }
    }, [shape.props.drawing])

    const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.beginPath()
        ctx.moveTo(x, y)
        setIsDrawing(true)
      }
    }

    const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isDrawing) return

      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.lineTo(x, y)

        if (currentTool === 'pen') {
          ctx.strokeStyle = currentColor
          ctx.lineWidth = currentSize
          ctx.lineCap = 'round'
          ctx.lineJoin = 'round'
          ctx.globalCompositeOperation = 'source-over'
        } else if (currentTool === 'eraser') {
          ctx.strokeStyle = shape.props.backgroundColor
          ctx.lineWidth = currentSize * 2
          ctx.lineCap = 'round'
          ctx.lineJoin = 'round'
          ctx.globalCompositeOperation = 'destination-out'
        } else if (currentTool === 'highlighter') {
          ctx.strokeStyle = currentColor
          ctx.lineWidth = currentSize * 3
          ctx.lineCap = 'round'
          ctx.lineJoin = 'round'
          ctx.globalAlpha = 0.3
          ctx.globalCompositeOperation = 'source-over'
        }

        ctx.stroke()
        ctx.globalAlpha = 1
      }
    }

    const stopDrawing = () => {
      if (isDrawing) {
        const canvas = canvasRef.current
        if (canvas) {
          // Save the drawing
          const dataUrl = canvas.toDataURL()
          editor.updateShape({
            id: shape.id,
            type: 'freeform-drawing-node',
            props: {
              drawing: dataUrl,
            },
          })
        }
        setIsDrawing(false)
      }
    }

    const clearCanvas = () => {
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          editor.updateShape({
            id: shape.id,
            type: 'freeform-drawing-node',
            props: {
              drawing: '',
            },
          })
        }
      }
    }

    const toolConfig = {
      pen: { icon: '✏️', color: '#3b82f6' },
      eraser: { icon: '🧹', color: '#ef4444' },
      highlighter: { icon: '🖍️', color: '#f59e0b' },
    }

    return (
      <HTMLContainer
        style={{
          width: shape.props.w,
          height: shape.props.h,
          pointerEvents: 'all',
        }}
      >
        <div
          style={{
            width: '100%',
            height: '100%',
            background: '#1e293b',
            borderRadius: '12px',
            border: '2px solid #334155',
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Toolbar */}
          <div
            style={{
              padding: '8px 12px',
              background: '#0f172a',
              borderBottom: '1px solid #334155',
              display: 'flex',
              gap: '8px',
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            {/* Tool Selection */}
            <div style={{ display: 'flex', gap: '4px' }}>
              {(['pen', 'eraser', 'highlighter'] as const).map((tool) => (
                <button
                  key={tool}
                  onClick={() => setCurrentTool(tool)}
                  style={{
                    padding: '6px 12px',
                    background: currentTool === tool ? toolConfig[tool].color : '#334155',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (currentTool !== tool) {
                      e.currentTarget.style.background = '#475569'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (currentTool !== tool) {
                      e.currentTarget.style.background = '#334155'
                    }
                  }}
                >
                  <span>{toolConfig[tool].icon}</span>
                </button>
              ))}
            </div>

            {/* Color Picker */}
            {currentTool !== 'eraser' && (
              <input
                type="color"
                value={currentColor}
                onChange={(e) => setCurrentColor(e.target.value)}
                style={{
                  width: '32px',
                  height: '32px',
                  border: '2px solid #334155',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              />
            )}

            {/* Brush Size */}
            <input
              type="range"
              min="1"
              max="20"
              value={currentSize}
              onChange={(e) => setCurrentSize(parseInt(e.target.value))}
              style={{
                width: '80px',
                accentColor: '#3b82f6',
              }}
            />
            <span style={{ fontSize: '11px', color: '#94a3b8', minWidth: '30px' }}>
              {currentSize}px
            </span>

            {/* Clear Button */}
            <button
              onClick={clearCanvas}
              style={{
                padding: '6px 12px',
                background: '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 500,
                marginLeft: 'auto',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#b91c1c'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#dc2626'
              }}
            >
              Clear
            </button>
          </div>

          {/* Canvas Area */}
          <div
            style={{
              flex: 1,
              position: 'relative',
              background: shape.props.backgroundColor,
              overflow: 'hidden',
            }}
          >
            <canvas
              ref={canvasRef}
              width={shape.props.w - 4}
              height={shape.props.h - 100}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              style={{
                cursor: currentTool === 'eraser' ? 'cell' : 'crosshair',
                width: '100%',
                height: '100%',
              }}
            />
          </div>

          {/* Footer */}
          <div
            style={{
              padding: '8px 12px',
              background: '#1e293b',
              borderTop: '1px solid #334155',
            }}
          >
            <div
              style={{
                fontSize: '12px',
                color: '#e2e8f0',
                fontWeight: 500,
              }}
            >
              {shape.props.description}
            </div>
            {shape.props.tags.length > 0 && (
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                {shape.props.tags.map((tag, i) => (
                  <span
                    key={i}
                    style={{
                      padding: '2px 8px',
                      background: '#334155',
                      color: '#94a3b8',
                      borderRadius: '4px',
                      fontSize: '10px',
                    }}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: FreeformDrawingNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
