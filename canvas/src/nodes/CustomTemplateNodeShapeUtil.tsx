import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'
import { useState } from 'react'

// Custom Template node for customizable outreach templates
export type CustomTemplateNodeShape = TLBaseShape<
  'custom-template-node',
  {
    w: number
    h: number
    templateName: string
    templateType: 'email' | 'linkedin' | 'twitter' | 'instagram' | 'custom'
    subject?: string
    body: string
    variables: string[] // Dynamic variables like {name}, {company}, etc.
    tone: 'professional' | 'casual' | 'friendly' | 'formal'
    cta?: string // Call to action
    tags: string[]
    color: string
  }
>

export class CustomTemplateNodeShapeUtil extends BaseBoxShapeUtil<CustomTemplateNodeShape> {
  static override type = 'custom-template-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    templateName: T.string,
    templateType: T.string,
    subject: T.string,
    body: T.string,
    variables: T.arrayOf(T.string),
    tone: T.string,
    cta: T.string,
    tags: T.arrayOf(T.string),
    color: T.string,
  }

  getDefaultProps(): CustomTemplateNodeShape['props'] {
    return {
      w: 400,
      h: 500,
      templateName: 'New Template',
      templateType: 'email',
      subject: '',
      body: 'Hi {name},\n\nI hope this message finds you well...',
      variables: ['{name}'],
      tone: 'professional',
      cta: '',
      tags: [],
      color: '#3b82f6',
    }
  }

  component(shape: CustomTemplateNodeShape) {
    const [isEditing, setIsEditing] = useState(false)
    const [editedBody, setEditedBody] = useState(shape.props.body)
    const [showVariables, setShowVariables] = useState(false)
    const editor = this.editor

    const saveTemplate = () => {
      // Extract variables from the body
      const variableRegex = /\{([^}]+)\}/g
      const extractedVars = [...editedBody.matchAll(variableRegex)].map((match) => match[0])
      const uniqueVars = [...new Set(extractedVars)]

      editor.updateShape({
        id: shape.id,
        type: 'custom-template-node',
        props: {
          body: editedBody,
          variables: uniqueVars,
        },
      })
      setIsEditing(false)

      // Trigger template save event
      window.dispatchEvent(
        new CustomEvent('save-template', {
          detail: {
            nodeId: shape.id,
            template: {
              name: shape.props.templateName,
              type: shape.props.templateType,
              subject: shape.props.subject,
              body: editedBody,
              variables: uniqueVars,
              tone: shape.props.tone,
              cta: shape.props.cta,
            },
          },
        })
      )
    }

    const templateTypeConfig = {
      email: { icon: '📧', label: 'Email', color: '#22c55e' },
      linkedin: { icon: '💼', label: 'LinkedIn', color: '#0077b5' },
      twitter: { icon: '🐦', label: 'Twitter', color: '#1da1f2' },
      instagram: { icon: '📸', label: 'Instagram', color: '#e4405f' },
      custom: { icon: '✨', label: 'Custom', color: '#8b5cf6' },
    }

    const toneConfig = {
      professional: { icon: '👔', color: '#3b82f6' },
      casual: { icon: '😊', color: '#22c55e' },
      friendly: { icon: '🤝', color: '#f59e0b' },
      formal: { icon: '🎩', color: '#6366f1' },
    }

    const config = templateTypeConfig[shape.props.templateType] || templateTypeConfig.custom
    const toneInfo = toneConfig[shape.props.tone] || toneConfig.professional

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
            border: `2px solid ${shape.props.color}`,
            boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '12px',
              background: shape.props.color,
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>{config.icon}</span>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600 }}>
                  {shape.props.templateName}
                </div>
                <div style={{ fontSize: '11px', opacity: 0.9 }}>
                  {config.label} Template
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ fontSize: '14px' }}>{toneInfo.icon}</span>
              <span style={{ fontSize: '11px', textTransform: 'capitalize' }}>
                {shape.props.tone}
              </span>
            </div>
          </div>

          {/* Subject (for email) */}
          {shape.props.templateType === 'email' && (
            <div
              style={{
                padding: '10px 12px',
                background: '#0f172a',
                borderBottom: '1px solid #334155',
              }}
            >
              <div style={{ fontSize: '11px', color: '#94a3b8', marginBottom: '4px' }}>
                Subject:
              </div>
              <div style={{ fontSize: '13px', color: '#e2e8f0', fontWeight: 500 }}>
                {shape.props.subject || 'No subject'}
              </div>
            </div>
          )}

          {/* Template Body */}
          <div
            style={{
              flex: 1,
              padding: '12px',
              background: '#0f172a',
              overflow: 'auto',
            }}
          >
            {isEditing ? (
              <textarea
                value={editedBody}
                onChange={(e) => setEditedBody(e.target.value)}
                style={{
                  width: '100%',
                  height: '100%',
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  padding: '8px',
                  color: '#e2e8f0',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  lineHeight: '1.6',
                  resize: 'none',
                }}
                placeholder="Write your template here... Use {variable} for dynamic content"
              />
            ) : (
              <div
                style={{
                  color: '#e2e8f0',
                  fontSize: '12px',
                  lineHeight: '1.8',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'system-ui',
                }}
              >
                {shape.props.body.split(/(\{[^}]+\})/).map((part, i) => {
                  if (part.match(/\{[^}]+\}/)) {
                    return (
                      <span
                        key={i}
                        style={{
                          background: '#3b82f6',
                          color: 'white',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '11px',
                          fontWeight: 600,
                        }}
                      >
                        {part}
                      </span>
                    )
                  }
                  return <span key={i}>{part}</span>
                })}
              </div>
            )}
          </div>

          {/* Variables & CTA */}
          <div
            style={{
              padding: '10px 12px',
              background: '#1e293b',
              borderTop: '1px solid #334155',
            }}
          >
            {/* Variables */}
            {shape.props.variables.length > 0 && (
              <div style={{ marginBottom: '8px' }}>
                <button
                  onClick={() => setShowVariables(!showVariables)}
                  style={{
                    fontSize: '11px',
                    color: '#94a3b8',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    marginBottom: '6px',
                    padding: 0,
                  }}
                >
                  <span>{showVariables ? '▼' : '▶'}</span>
                  <span>Variables ({shape.props.variables.length})</span>
                </button>
                {showVariables && (
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    {shape.props.variables.map((variable, i) => (
                      <span
                        key={i}
                        style={{
                          padding: '3px 8px',
                          background: '#3b82f6',
                          color: 'white',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: 600,
                        }}
                      >
                        {variable}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* CTA */}
            {shape.props.cta && (
              <div
                style={{
                  padding: '8px',
                  background: '#22c55e',
                  color: 'white',
                  borderRadius: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  textAlign: 'center',
                  marginBottom: '8px',
                }}
              >
                🎯 {shape.props.cta}
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
            <div style={{ display: 'flex', gap: '6px' }}>
              {isEditing ? (
                <>
                  <button
                    onClick={saveTemplate}
                    style={{
                      flex: 1,
                      padding: '8px',
                      background: '#22c55e',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: 600,
                    }}
                  >
                    💾 Save
                  </button>
                  <button
                    onClick={() => {
                      setEditedBody(shape.props.body)
                      setIsEditing(false)
                    }}
                    style={{
                      flex: 1,
                      padding: '8px',
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: 600,
                    }}
                  >
                    ✕ Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  style={{
                    flex: 1,
                    padding: '8px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#2563eb'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#3b82f6'
                  }}
                >
                  ✏️ Edit Template
                </button>
              )}
            </div>
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: CustomTemplateNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
