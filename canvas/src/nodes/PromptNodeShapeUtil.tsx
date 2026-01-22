import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'
import { useState, useRef, useEffect } from 'react'

// Prompt node for natural language instructions
export type PromptNodeShape = TLBaseShape<
  'prompt-node',
  {
    w: number
    h: number
    text: string
    category: 'instruction' | 'question' | 'condition' | 'decision' | 'idea'
    aiInterpretation?: string
    mappedSkill?: string
    priority: number
    color: string
    isMarkdown: boolean
  }
>

export class PromptNodeShapeUtil extends BaseBoxShapeUtil<PromptNodeShape> {
  static override type = 'prompt-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    text: T.string,
    category: T.string,
    aiInterpretation: T.string,
    mappedSkill: T.string,
    priority: T.number,
    color: T.string,
    isMarkdown: T.boolean,
  }

  getDefaultProps(): PromptNodeShape['props'] {
    return {
      w: 280,
      h: 180,
      text: 'Write your prompt here...',
      category: 'instruction',
      aiInterpretation: '',
      mappedSkill: '',
      priority: 1,
      color: '#fef08a', // Yellow sticky note
      isMarkdown: false,
    }
  }

  component(shape: PromptNodeShape) {
    const [isEditing, setIsEditing] = useState(false)
    const [localText, setLocalText] = useState(shape.props.text)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const editor = this.editor

    useEffect(() => {
      setLocalText(shape.props.text)
    }, [shape.props.text])

    const categoryConfig = {
      instruction: { icon: '📝', label: 'Instruction', border: '#facc15' },
      question: { icon: '❓', label: 'Question', border: '#60a5fa' },
      condition: { icon: '🔀', label: 'Condition', border: '#a78bfa' },
      decision: { icon: '⚖️', label: 'Decision', border: '#f472b6' },
      idea: { icon: '💡', label: 'Idea', border: '#34d399' },
    }

    const config = categoryConfig[shape.props.category] || categoryConfig.instruction

    const handleDoubleClick = () => {
      setIsEditing(true)
      setTimeout(() => textareaRef.current?.focus(), 0)
    }

    const handleBlur = () => {
      setIsEditing(false)
      if (localText !== shape.props.text) {
        editor.updateShape({
          id: shape.id,
          type: 'prompt-node',
          props: { text: localText },
        })
      }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleBlur()
      }
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
            background: shape.props.color,
            borderRadius: '8px',
            border: `3px solid ${config.border}`,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            transform: 'rotate(-1deg)',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          }}
          onDoubleClick={handleDoubleClick}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'rotate(0deg) scale(1.02)'
            e.currentTarget.style.boxShadow =
              '0 8px 24px rgba(0,0,0,0.2), 0 4px 8px rgba(0,0,0,0.15)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'rotate(-1deg) scale(1)'
            e.currentTarget.style.boxShadow =
              '0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1)'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '8px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              borderBottom: `2px solid ${config.border}`,
              background: 'rgba(0,0,0,0.03)',
            }}
          >
            <span style={{ fontSize: '16px' }}>{config.icon}</span>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: '#1f2937',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}
            >
              {config.label}
            </span>
            {shape.props.priority > 1 && (
              <span
                style={{
                  marginLeft: 'auto',
                  padding: '2px 6px',
                  background: '#ef4444',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: 'bold',
                }}
              >
                P{shape.props.priority}
              </span>
            )}
          </div>

          {/* Content */}
          <div style={{ flex: 1, padding: '12px', overflow: 'auto' }}>
            {isEditing ? (
              <textarea
                ref={textareaRef}
                value={localText}
                onChange={(e) => setLocalText(e.target.value)}
                onBlur={handleBlur}
                onKeyDown={handleKeyDown}
                style={{
                  width: '100%',
                  height: '100%',
                  border: 'none',
                  outline: 'none',
                  background: 'transparent',
                  fontSize: '14px',
                  fontFamily: "'Inter', sans-serif",
                  color: '#1f2937',
                  resize: 'none',
                  lineHeight: '1.5',
                }}
                placeholder="Write your prompt here..."
              />
            ) : (
              <div
                style={{
                  fontSize: '14px',
                  fontFamily: "'Inter', sans-serif",
                  color: '#1f2937',
                  lineHeight: '1.5',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {shape.props.text || 'Double-click to edit...'}
              </div>
            )}
          </div>

          {/* AI Interpretation Footer */}
          {shape.props.aiInterpretation && (
            <div
              style={{
                padding: '8px 12px',
                borderTop: `2px solid ${config.border}`,
                background: 'rgba(99, 102, 241, 0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <span style={{ fontSize: '12px' }}>🤖</span>
              <span
                style={{
                  fontSize: '11px',
                  color: '#4f46e5',
                  fontStyle: 'italic',
                }}
              >
                {shape.props.aiInterpretation}
              </span>
            </div>
          )}

          {/* Mapped Skill Badge */}
          {shape.props.mappedSkill && (
            <div
              style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                padding: '4px 8px',
                background: '#10b981',
                color: 'white',
                borderRadius: '12px',
                fontSize: '10px',
                fontWeight: 'bold',
                boxShadow: '0 2px 8px rgba(16, 185, 129, 0.4)',
              }}
            >
              {shape.props.mappedSkill}
            </div>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: PromptNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={8} ry={8} />
  }
}
