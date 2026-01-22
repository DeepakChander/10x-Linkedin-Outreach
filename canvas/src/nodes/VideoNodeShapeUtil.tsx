import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'
import { useState, useRef } from 'react'

// Video node for video content with AI analysis
export type VideoNodeShape = TLBaseShape<
  'video-node',
  {
    w: number
    h: number
    videoUrl: string
    sourceUrl?: string  // YouTube, LinkedIn, Instagram, Reddit URL
    description: string
    caption?: string
    duration?: number
    thumbnail?: string
    aiVideoAnalysis?: string
    transcript?: string
    clips?: string[]
    summary?: string
    tags: string[]
    useInWorkflow: 'context' | 'attachment' | 'reference'
    autoplay: boolean
    loop: boolean
    muted: boolean
    processing: boolean
  }
>

export class VideoNodeShapeUtil extends BaseBoxShapeUtil<VideoNodeShape> {
  static override type = 'video-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    videoUrl: T.string,
    sourceUrl: T.string,
    description: T.string,
    caption: T.string,
    duration: T.number,
    thumbnail: T.string,
    aiVideoAnalysis: T.string,
    transcript: T.string,
    clips: T.arrayOf(T.string),
    summary: T.string,
    tags: T.arrayOf(T.string),
    useInWorkflow: T.string,
    autoplay: T.boolean,
    loop: T.boolean,
    muted: T.boolean,
    processing: T.boolean,
  }

  getDefaultProps(): VideoNodeShape['props'] {
    return {
      w: 480,
      h: 500,
      videoUrl: '',
      sourceUrl: '',
      description: 'Drag & drop video or paste URL',
      caption: '',
      duration: 0,
      thumbnail: '',
      aiVideoAnalysis: '',
      transcript: '',
      clips: [],
      summary: '',
      tags: [],
      useInWorkflow: 'reference',
      autoplay: false,
      loop: false,
      muted: true,
      processing: false,
    }
  }

  component(shape: VideoNodeShape) {
    const [isDragging, setIsDragging] = useState(false)
    const [showAnalysis, setShowAnalysis] = useState(false)
    const [showTranscript, setShowTranscript] = useState(false)
    const [showClips, setShowClips] = useState(false)
    const [isPlaying, setIsPlaying] = useState(false)
    const [urlInput, setUrlInput] = useState(shape.props.sourceUrl || '')
    const fileInputRef = useRef<HTMLInputElement>(null)
    const videoRef = useRef<HTMLVideoElement>(null)
    const editor = this.editor

    const handleDrop = (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const files = Array.from(e.dataTransfer.files)
      const videoFile = files.find((f) => f.type.startsWith('video/'))

      if (videoFile) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const dataUrl = event.target?.result as string
          editor.updateShape({
            id: shape.id,
            type: 'video-node',
            props: {
              videoUrl: dataUrl,
              description: videoFile.name,
            },
          })

          // Trigger AI video analysis
          window.dispatchEvent(
            new CustomEvent('analyze-video', {
              detail: { nodeId: shape.id, videoUrl: dataUrl },
            })
          )
        }
        reader.readAsDataURL(videoFile)
      }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file && file.type.startsWith('video/')) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const dataUrl = event.target?.result as string
          editor.updateShape({
            id: shape.id,
            type: 'video-node',
            props: {
              videoUrl: dataUrl,
              description: file.name,
            },
          })

          // Trigger AI video analysis
          window.dispatchEvent(
            new CustomEvent('analyze-video', {
              detail: { nodeId: shape.id, videoUrl: dataUrl },
            })
          )
        }
        reader.readAsDataURL(file)
      }
    }

    const togglePlay = () => {
      if (videoRef.current) {
        if (isPlaying) {
          videoRef.current.pause()
        } else {
          videoRef.current.play()
        }
        setIsPlaying(!isPlaying)
      }
    }

    const processURL = async () => {
      if (!urlInput.trim()) return

      // Update node to show processing state
      editor.updateShape({
        id: shape.id,
        type: 'video-node',
        props: {
          sourceUrl: urlInput,
          processing: true,
          description: 'Processing video...'
        },
      })

      // Trigger video processing via WebSocket/API
      window.dispatchEvent(
        new CustomEvent('process-video-url', {
          detail: {
            nodeId: shape.id,
            url: urlInput,
          },
        })
      )
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
          {/* Video Display Area */}
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
            {shape.props.videoUrl ? (
              <div style={{ width: '100%', height: '100%', position: 'relative' }}>
                <video
                  ref={videoRef}
                  src={shape.props.videoUrl}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                  }}
                  autoPlay={shape.props.autoplay}
                  loop={shape.props.loop}
                  muted={shape.props.muted}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />
                {/* Play/Pause Overlay */}
                <button
                  onClick={togglePlay}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'rgba(0,0,0,0.6)',
                    border: '2px solid white',
                    color: 'white',
                    fontSize: '24px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(0,0,0,0.8)'
                    e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1.1)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(0,0,0,0.6)'
                    e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1)'
                  }}
                >
                  {isPlaying ? '⏸' : '▶'}
                </button>
              </div>
            ) : (
              <div
                style={{
                  textAlign: 'center',
                  padding: '20px',
                  color: '#64748b',
                }}
              >
                <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎥</div>
                <div style={{ fontSize: '14px', marginBottom: '8px' }}>
                  Drag & drop video here
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
                  accept="video/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            )}

            {/* AI Video Analysis Overlay */}
            {shape.props.aiVideoAnalysis && showAnalysis && (
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
                  <span style={{ fontWeight: 600 }}>AI Video Analysis:</span>
                </div>
                {shape.props.aiVideoAnalysis}
              </div>
            )}
          </div>

          {/* URL Input Section */}
          {!shape.props.videoUrl && (
            <div
              style={{
                padding: '12px',
                background: '#0f172a',
                borderBottom: '1px solid #334155',
              }}
            >
              <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '6px' }}>
                Or paste URL (YouTube, LinkedIn, Instagram, Reddit):
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <input
                  type="text"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://youtube.com/watch?v=..."
                  style={{
                    flex: 1,
                    padding: '8px',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    color: '#e2e8f0',
                    fontSize: '12px',
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      processURL()
                    }
                  }}
                />
                <button
                  onClick={processURL}
                  disabled={!urlInput.trim() || shape.props.processing}
                  style={{
                    padding: '8px 16px',
                    background: shape.props.processing ? '#6b7280' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: shape.props.processing ? 'wait' : 'pointer',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                >
                  {shape.props.processing ? '⏳' : '🚀'} Process
                </button>
              </div>
            </div>
          )}

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

            {/* Caption & Duration */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              {shape.props.caption && (
                <div
                  style={{
                    fontSize: '11px',
                    color: '#94a3b8',
                    fontStyle: 'italic',
                  }}
                >
                  {shape.props.caption}
                </div>
              )}
              {shape.props.duration > 0 && (
                <div
                  style={{
                    fontSize: '11px',
                    color: '#94a3b8',
                  }}
                >
                  {Math.floor(shape.props.duration / 60)}:{String(Math.floor(shape.props.duration % 60)).padStart(2, '0')}
                </div>
              )}
            </div>

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
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
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
              {shape.props.aiVideoAnalysis && (
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

              {/* Transcript Toggle */}
              {shape.props.transcript && (
                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  style={{
                    padding: '4px 8px',
                    background: showTranscript ? '#10b981' : '#334155',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '10px',
                    fontWeight: 500,
                  }}
                >
                  📝 {showTranscript ? 'Hide' : 'Show'} Transcript
                </button>
              )}

              {/* Clips Toggle */}
              {shape.props.clips && shape.props.clips.length > 0 && (
                <button
                  onClick={() => setShowClips(!showClips)}
                  style={{
                    padding: '4px 8px',
                    background: showClips ? '#f59e0b' : '#334155',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '10px',
                    fontWeight: 500,
                  }}
                >
                  ✂️ {shape.props.clips.length} Clips
                </button>
              )}
            </div>

            {/* Transcript Panel */}
            {showTranscript && shape.props.transcript && (
              <div
                style={{
                  marginTop: '8px',
                  padding: '8px',
                  background: '#0f172a',
                  borderRadius: '6px',
                  maxHeight: '150px',
                  overflow: 'auto',
                  fontSize: '11px',
                  color: '#e2e8f0',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {shape.props.transcript}
              </div>
            )}

            {/* Clips Panel */}
            {showClips && shape.props.clips && shape.props.clips.length > 0 && (
              <div
                style={{
                  marginTop: '8px',
                  padding: '8px',
                  background: '#0f172a',
                  borderRadius: '6px',
                }}
              >
                <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '6px' }}>
                  Video Clips ({shape.props.clips.length}):
                </div>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {shape.props.clips.map((clip, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '4px 8px',
                        background: '#1e293b',
                        borderRadius: '4px',
                        fontSize: '10px',
                        color: '#f59e0b',
                      }}
                    >
                      Clip {i + 1}
                    </div>
                  ))}
                </div>
              </div>
            )}
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
              📥 Drop video here
            </div>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: VideoNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
