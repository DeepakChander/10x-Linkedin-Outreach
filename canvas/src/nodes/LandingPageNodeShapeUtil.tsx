import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'

// Landing Page node for website/page mockups
export type LandingPageNodeShape = TLBaseShape<
  'landing-page-node',
  {
    w: number
    h: number
    pageName: string
    headline: string
    subheadline: string
    ctaText: string
    sections: Array<{ title: string; content: string }>
    heroImageUrl?: string
    colorScheme: 'blue' | 'purple' | 'green' | 'orange' | 'minimal'
    hasNavbar: boolean
    hasFooter: boolean
  }
>

export class LandingPageNodeShapeUtil extends BaseBoxShapeUtil<LandingPageNodeShape> {
  static override type = 'landing-page-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    pageName: T.string,
    headline: T.string,
    subheadline: T.string,
    ctaText: T.string,
    sections: T.arrayOf(T.any),
    heroImageUrl: T.string,
    colorScheme: T.string,
    hasNavbar: T.boolean,
    hasFooter: T.boolean,
  }

  getDefaultProps(): LandingPageNodeShape['props'] {
    return {
      w: 360,
      h: 640,
      pageName: 'Landing Page',
      headline: 'Transform Your Business',
      subheadline: 'The ultimate solution for modern teams',
      ctaText: 'Get Started Free',
      sections: [
        { title: 'Features', content: 'Amazing features that you will love' },
        { title: 'Pricing', content: 'Simple and transparent pricing' },
      ],
      heroImageUrl: '',
      colorScheme: 'blue',
      hasNavbar: true,
      hasFooter: true,
    }
  }

  component(shape: LandingPageNodeShape) {
    const colorSchemes = {
      blue: {
        primary: '#3b82f6',
        secondary: '#60a5fa',
        bg: '#eff6ff',
        text: '#1e3a8a',
      },
      purple: {
        primary: '#8b5cf6',
        secondary: '#a78bfa',
        bg: '#f5f3ff',
        text: '#5b21b6',
      },
      green: {
        primary: '#10b981',
        secondary: '#34d399',
        bg: '#ecfdf5',
        text: '#065f46',
      },
      orange: {
        primary: '#f97316',
        secondary: '#fb923c',
        bg: '#fff7ed',
        text: '#9a3412',
      },
      minimal: {
        primary: '#1f2937',
        secondary: '#4b5563',
        bg: '#ffffff',
        text: '#111827',
      },
    }

    const colors = colorSchemes[shape.props.colorScheme] || colorSchemes.blue

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
            background: 'white',
            borderRadius: '12px',
            border: '2px solid #e5e7eb',
            boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
          }}
        >
          {/* Browser Chrome */}
          <div
            style={{
              height: '28px',
              background: '#f3f4f6',
              borderBottom: '1px solid #d1d5db',
              display: 'flex',
              alignItems: 'center',
              padding: '0 10px',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', gap: '4px' }}>
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#ef4444',
                }}
              />
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#fbbf24',
                }}
              />
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: '#22c55e',
                }}
              />
            </div>
            <div
              style={{
                flex: 1,
                height: '16px',
                background: 'white',
                borderRadius: '4px',
                fontSize: '9px',
                padding: '0 8px',
                display: 'flex',
                alignItems: 'center',
                color: '#6b7280',
              }}
            >
              🔒 {shape.props.pageName.toLowerCase().replace(/\s+/g, '-')}.com
            </div>
          </div>

          {/* Page Content */}
          <div
            style={{
              flex: 1,
              overflow: 'auto',
              background: colors.bg,
            }}
          >
            {/* Navbar */}
            {shape.props.hasNavbar && (
              <div
                style={{
                  height: '50px',
                  background: 'white',
                  borderBottom: '1px solid #e5e7eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0 20px',
                }}
              >
                <div
                  style={{
                    fontWeight: 'bold',
                    fontSize: '14px',
                    color: colors.primary,
                  }}
                >
                  {shape.props.pageName}
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ fontSize: '9px', color: '#6b7280' }}>Features</div>
                  <div style={{ fontSize: '9px', color: '#6b7280' }}>Pricing</div>
                  <div style={{ fontSize: '9px', color: '#6b7280' }}>About</div>
                </div>
              </div>
            )}

            {/* Hero Section */}
            <div
              style={{
                padding: '40px 20px',
                textAlign: 'center',
                background: `linear-gradient(135deg, ${colors.primary}15 0%, ${colors.secondary}15 100%)`,
              }}
            >
              {/* Hero Image */}
              {shape.props.heroImageUrl && (
                <div
                  style={{
                    width: '80px',
                    height: '80px',
                    margin: '0 auto 16px',
                    borderRadius: '50%',
                    overflow: 'hidden',
                    border: `3px solid ${colors.primary}`,
                  }}
                >
                  <img
                    src={shape.props.heroImageUrl}
                    alt="Hero"
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                </div>
              )}

              {/* Headline */}
              <h1
                style={{
                  fontSize: '24px',
                  fontWeight: 'bold',
                  color: colors.text,
                  marginBottom: '8px',
                  lineHeight: '1.2',
                }}
              >
                {shape.props.headline}
              </h1>

              {/* Subheadline */}
              <p
                style={{
                  fontSize: '13px',
                  color: colors.text,
                  opacity: 0.7,
                  marginBottom: '20px',
                }}
              >
                {shape.props.subheadline}
              </p>

              {/* CTA Button */}
              <button
                style={{
                  padding: '10px 24px',
                  background: colors.primary,
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  boxShadow: `0 4px 12px ${colors.primary}40`,
                }}
              >
                {shape.props.ctaText}
              </button>
            </div>

            {/* Content Sections */}
            {shape.props.sections.map((section, i) => (
              <div
                key={i}
                style={{
                  padding: '24px 20px',
                  background: i % 2 === 0 ? 'white' : colors.bg,
                  borderTop: '1px solid #e5e7eb',
                }}
              >
                <h3
                  style={{
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: colors.text,
                    marginBottom: '8px',
                  }}
                >
                  {section.title}
                </h3>
                <p
                  style={{
                    fontSize: '12px',
                    color: colors.text,
                    opacity: 0.7,
                    lineHeight: '1.5',
                  }}
                >
                  {section.content}
                </p>
              </div>
            ))}

            {/* Footer */}
            {shape.props.hasFooter && (
              <div
                style={{
                  padding: '20px',
                  background: colors.text,
                  color: 'white',
                  textAlign: 'center',
                  fontSize: '10px',
                  opacity: 0.8,
                }}
              >
                © 2024 {shape.props.pageName}. All rights reserved.
              </div>
            )}
          </div>

          {/* Label Badge */}
          <div
            style={{
              position: 'absolute',
              top: '36px',
              left: '8px',
              background: colors.primary,
              color: 'white',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '10px',
              fontWeight: 'bold',
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
              zIndex: 10,
            }}
          >
            🎨 Landing Page
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: LandingPageNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
