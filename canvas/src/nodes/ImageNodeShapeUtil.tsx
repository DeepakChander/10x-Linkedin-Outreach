import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'
import { useState, useRef } from 'react'

// Image node for visual content with AI analysis
export type ImageNodeShape = TLBaseShape<
  'image-node',
  {
    w: number
    h: number
    imageUrl: string
    description: string
    caption?: string
    aiVisionAnalysis?: string
    tags: string[]
    useInWorkflow: 'context' | 'attachment' | 'reference'
    opacity: number
  }
>

export class ImageNodeShapeUtil extends BaseBoxShapeUtil<ImageNodeShape> {
  static override type = 'image-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    imageUrl: T.string,
    description: T.string,
    caption: T.string,
    aiVisionAnalysis: T.string,
    tags: T.arrayOf(T.string),
    useInWorkflow: T.string,
    opacity: T.number,
  }

  getDefaultProps(): ImageNodeShape['props'] {
    return {
      w: 320,
      h: 400,
      imageUrl: '',
      description: 'Drag & drop an image here',
      caption: '',
      aiVisionAnalysis: '',
      tags: [],
      useInWorkflow: 'reference',
      opacity: 1,
    }
  }

  component(shape: ImageNodeShape) {
    const [isDragging, setIsDragging] = useState(false)
    const [showAnalysis, setShowAnalysis] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const editor = this.editor

    const handleDrop = (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      const imageFile = files.find((f) => f.type.startsWith('image/'))

      if (imageFile) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const dataUrl = event.target?.result as string
          editor.updateShape({
            id: shape.id,
            type: 'image-node',
            props: {
              imageUrl: dataUrl,
              description: imageFile.name,
            },
          })

          // Trigger AI vision analysis
          window.dispatchEvent(
            new CustomEvent('analyze-image', {
              detail: { nodeId: shape.id, imageUrl: dataUrl },
            })
          )
        }
        reader.readAsDataURL(imageFile)
      }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const dataUrl = event.target?.result as string
          editor.updateShape({
            id: shape.id,
            type: 'image-node',
            props: {
              imageUrl: dataUrl,
              description: file.name,
            },
          })

          // Trigger AI vision analysis
          window.dispatchEvent(
            new CustomEvent('analyze-image', {
              detail: { nodeId: shape.id, imageUrl: dataUrl },
            })
          )
        }
        reader.readAsDataURL(file)
      }
    }

    const usageConfig = {
      context: { color: '#8b5cf6', label: 'Context', icon: '🎯' },
      attachment: { color: '#f59e0b', label: 'Attachment', icon: '📎' },
      reference: { color: '#06b6d4', label: 'Reference', icon: '🔗' },
    }

    const config = usageConfig[shape.props.useInWorkflow] || usageConfig.reference

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
            border: isDragging ? '3px dashed #3b82f6' : '2px solid #334155',
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative',
          }}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          {/* Image Display Area */}
          <div
            style={{
              flex: 1,
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#0f172a',
              overflow: 'hidden',
            }}
          >
            {shape.props.imageUrl ? (
              <img
                src={shape.props.imageUrl}
                alt={shape.props.description}
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                  opacity: shape.props.opacity,
                }}
              />
            ) : (
              <div
                style={{
                  textAlign: 'center',
                  padding: '20px',
                  color: '#64748b',
                }}
              >
                <div style={{ fontSize: '48px', marginBottom: '12px' }}>🖼️</div>
                <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                  Drag & drop image here
                </div>
                <div style={{ fontSize: '12px', color: '#475569' }}>or</div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    marginTop: '12px',
                    padding: '8px 16px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: 500,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#2563eb'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#3b82f6'
                  }}
                >
                  Browse Files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            )}

            {/* AI Vision Analysis Overlay */}
            {shape.props.aiVisionAnalysis && showAnalysis && (
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '12px',
                  background: 'rgba(0,0,0,0.9)',
                  backdropFilter: 'blur(8px)',
                  color: 'white',
                  fontSize: '12px',
                  lineHeight: '1.5',
                  maxHeight: '50%',
                  overflow: 'auto',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <span>🤖</span>
                  <span style={{ fontWeight: 600 }}>AI Vision Analysis:</span>
                </div>
                {shape.props.aiVisionAnalysis}
              </div>
            )}
          </div>

          {/* Footer with Description */}
          <div
            style={{
              padding: '10px 12px',
              background: '#1e293b',
              borderTop: '1px solid #334155',
            }}
          >
            {/* Description */}
            <div
              style={{
                fontSize: '13px',
                color: '#e2e8f0',
                marginBottom: '8px',
                fontWeight: 500,
              }}
            >
              {shape.props.description}
            </div>

            {/* Caption */}
            {shape.props.caption && (
              <div
                style={{
                  fontSize: '11px',
                  color: '#94a3b8',
                  fontStyle: 'italic',
                  marginBottom: '8px',
                }}
              >
                {shape.props.caption}
              </div>
            )}

            {/* Tags */}
            {shape.props.tags.length > 0 && (
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginBottom: '8px' }}>
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

            {/* Actions */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {/* Usage Type Badge */}
              <div
                style={{
                  padding: '4px 8px',
                  background: config.color,
                  color: 'white',
                  borderRadius: '6px',
                  fontSize: '10px',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <span>{config.icon}</span>
                <span>{config.label}</span>
              </div>

              {/* AI Analysis Toggle */}
              {shape.props.aiVisionAnalysis && (
                <button
                  onClick={() => setShowAnalysis(!showAnalysis)}
                  style={{
                    padding: '4px 8px',
                    background: showAnalysis ? '#6366f1' : '#334155',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '10px',
                    fontWeight: 500,
                  }}
                >
                  {showAnalysis ? 'Hide' : 'Show'} AI Analysis
                </button>
              )}
            </div>
          </div>

          {/* Drag Overlay */}
          {isDragging && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: 'rgba(59, 130, 246, 0.1)',
                backdropFilter: 'blur(4px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
                color: '#3b82f6',
                fontWeight: 600,
                pointerEvents: 'none',
              }}
            >
              📥 Drop image here
            </div>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: ImageNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
