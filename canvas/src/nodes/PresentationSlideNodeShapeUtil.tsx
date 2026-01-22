import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'

// Presentation Slide node for PPT mockups
export type PresentationSlideNodeShape = TLBaseShape<
  'presentation-slide-node',
  {
    w: number
    h: number
    slideNumber: number
    title: string
    content: string
    bulletPoints: string[]
    imageUrl?: string
    layout: 'title' | 'content' | 'image-left' | 'image-right' | 'full-image' | 'split'
    theme: 'light' | 'dark' | 'gradient-blue' | 'gradient-purple' | 'minimal'
    notes: string
  }
>

export class PresentationSlideNodeShapeUtil extends BaseBoxShapeUtil<PresentationSlideNodeShape> {
  static override type = 'presentation-slide-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    slideNumber: T.number,
    title: T.string,
    content: T.string,
    bulletPoints: T.arrayOf(T.string),
    imageUrl: T.string,
    layout: T.string,
    theme: T.string,
    notes: T.string,
  }

  getDefaultProps(): PresentationSlideNodeShape['props'] {
    return {
      w: 480,
      h: 340,
      slideNumber: 1,
      title: 'Slide Title',
      content: 'Main content goes here',
      bulletPoints: [],
      imageUrl: '',
      layout: 'title',
      theme: 'light',
      notes: '',
    }
  }

  component(shape: PresentationSlideNodeShape) {
    const themes = {
      light: {
        bg: '#ffffff',
        text: '#1f2937',
        accent: '#3b82f6',
        border: '#e5e7eb',
      },
      dark: {
        bg: '#1e293b',
        text: '#f1f5f9',
        accent: '#60a5fa',
        border: '#334155',
      },
      'gradient-blue': {
        bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        text: '#ffffff',
        accent: '#fbbf24',
        border: '#8b5cf6',
      },
      'gradient-purple': {
        bg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        text: '#1f2937',
        accent: '#8b5cf6',
        border: '#ec4899',
      },
      minimal: {
        bg: '#f9fafb',
        text: '#111827',
        accent: '#10b981',
        border: '#d1d5db',
      },
    }

    const theme = themes[shape.props.theme] || themes.light

    const renderContent = () => {
      switch (shape.props.layout) {
        case 'title':
          return (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
                padding: '40px',
              }}
            >
              <h1
                style={{
                  fontSize: '32px',
                  fontWeight: 'bold',
                  color: theme.text,
                  marginBottom: '16px',
                  lineHeight: '1.2',
                }}
              >
                {shape.props.title}
              </h1>
              {shape.props.content && (
                <p
                  style={{
                    fontSize: '18px',
                    color: theme.text,
                    opacity: 0.8,
                    maxWidth: '80%',
                  }}
                >
                  {shape.props.content}
                </p>
              )}
            </div>
          )

        case 'content':
          return (
            <div style={{ padding: '32px', height: '100%' }}>
              <h2
                style={{
                  fontSize: '24px',
                  fontWeight: 'bold',
                  color: theme.text,
                  marginBottom: '20px',
                  borderBottom: `3px solid ${theme.accent}`,
                  paddingBottom: '8px',
                }}
              >
                {shape.props.title}
              </h2>
              {shape.props.bulletPoints.length > 0 ? (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {shape.props.bulletPoints.map((point, i) => (
                    <li
                      key={i}
                      style={{
                        fontSize: '16px',
                        color: theme.text,
                        marginBottom: '12px',
                        paddingLeft: '24px',
                        position: 'relative',
                      }}
                    >
                      <span
                        style={{
                          position: 'absolute',
                          left: 0,
                          color: theme.accent,
                          fontWeight: 'bold',
                        }}
                      >
                        •
                      </span>
                      {point}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ fontSize: '16px', color: theme.text, lineHeight: '1.6' }}>
                  {shape.props.content}
                </p>
              )}
            </div>
          )

        case 'image-left':
        case 'image-right':
          return (
            <div
              style={{
                display: 'flex',
                flexDirection: shape.props.layout === 'image-left' ? 'row' : 'row-reverse',
                height: '100%',
              }}
            >
              <div
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(0,0,0,0.05)',
                  padding: '20px',
                }}
              >
                {shape.props.imageUrl ? (
                  <img
                    src={shape.props.imageUrl}
                    alt="Slide visual"
                    style={{
                      maxWidth: '100%',
                      maxHeight: '100%',
                      objectFit: 'contain',
                      borderRadius: '8px',
                    }}
                  />
                ) : (
                  <div style={{ fontSize: '48px', opacity: 0.3 }}>🖼️</div>
                )}
              </div>
              <div style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column' }}>
                <h2
                  style={{
                    fontSize: '22px',
                    fontWeight: 'bold',
                    color: theme.text,
                    marginBottom: '16px',
                  }}
                >
                  {shape.props.title}
                </h2>
                <div style={{ fontSize: '14px', color: theme.text, lineHeight: '1.6', flex: 1 }}>
                  {shape.props.content}
                </div>
              </div>
            </div>
          )

        case 'full-image':
          return (
            <div style={{ position: 'relative', height: '100%' }}>
              {shape.props.imageUrl ? (
                <img
                  src={shape.props.imageUrl}
                  alt="Full slide"
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
              ) : (
                <div
                  style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '64px',
                    opacity: 0.2,
                  }}
                >
                  🖼️
                </div>
              )}
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '24px',
                  background: 'rgba(0,0,0,0.7)',
                  backdropFilter: 'blur(8px)',
                }}
              >
                <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: 'white', margin: 0 }}>
                  {shape.props.title}
                </h2>
              </div>
            </div>
          )

        case 'split':
          return (
            <div style={{ display: 'flex', height: '100%' }}>
              <div
                style={{
                  flex: 1,
                  padding: '32px',
                  borderRight: `2px solid ${theme.border}`,
                }}
              >
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: theme.text }}>
                  Before
                </h3>
              </div>
              <div style={{ flex: 1, padding: '32px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: theme.accent }}>
                  After
                </h3>
              </div>
            </div>
          )

        default:
          return null
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
            position: 'relative',
            boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
            borderRadius: '8px',
            overflow: 'hidden',
            border: `3px solid ${theme.border}`,
          }}
        >
          {/* Slide Content */}
          <div
            style={{
              width: '100%',
              height: 'calc(100% - 32px)',
              background: theme.bg,
              position: 'relative',
            }}
          >
            {renderContent()}
          </div>

          {/* Footer with Slide Number */}
          <div
            style={{
              height: '32px',
              background: theme.accent,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0 16px',
              color: 'white',
              fontSize: '12px',
              fontWeight: 600,
            }}
          >
            <span>Slide {shape.props.slideNumber}</span>
            <span style={{ fontSize: '10px', opacity: 0.8 }}>
              {shape.props.layout.replace('-', ' ').toUpperCase()}
            </span>
          </div>

          {/* Speaker Notes Indicator */}
          {shape.props.notes && (
            <div
              style={{
                position: 'absolute',
                top: '8px',
                right: '8px',
                width: '24px',
                height: '24px',
                background: '#fbbf24',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              }}
              title={`Notes: ${shape.props.notes}`}
            >
              📝
            </div>
          )}
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: PresentationSlideNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={8} ry={8} />
  }
}
