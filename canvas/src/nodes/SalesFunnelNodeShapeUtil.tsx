import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'

// Sales Funnel node for conversion flow visualization
export type SalesFunnelNodeShape = TLBaseShape<
  'sales-funnel-node',
  {
    w: number
    h: number
    funnelName: string
    stages: Array<{
      name: string
      count: number
      conversionRate: number
      color: string
    }>
    showMetrics: boolean
    style: 'classic' | 'modern' | 'minimal'
  }
>

export class SalesFunnelNodeShapeUtil extends BaseBoxShapeUtil<SalesFunnelNodeShape> {
  static override type = 'sales-funnel-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    funnelName: T.string,
    stages: T.arrayOf(T.any),
    showMetrics: T.boolean,
    style: T.string,
  }

  getDefaultProps(): SalesFunnelNodeShape['props'] {
    return {
      w: 320,
      h: 480,
      funnelName: 'Sales Funnel',
      stages: [
        { name: 'Awareness', count: 10000, conversionRate: 100, color: '#3b82f6' },
        { name: 'Interest', count: 5000, conversionRate: 50, color: '#8b5cf6' },
        { name: 'Consideration', count: 2000, conversionRate: 40, color: '#ec4899' },
        { name: 'Intent', count: 800, conversionRate: 40, color: '#f59e0b' },
        { name: 'Purchase', count: 400, conversionRate: 50, color: '#10b981' },
      ],
      showMetrics: true,
      style: 'modern',
    }
  }

  component(shape: SalesFunnelNodeShape) {
    const maxCount = Math.max(...shape.props.stages.map((s) => s.count))

    const renderClassicFunnel = () => {
      return (
        <div style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Title */}
          <h3
            style={{
              fontSize: '18px',
              fontWeight: 'bold',
              color: '#1f2937',
              marginBottom: '20px',
              textAlign: 'center',
            }}
          >
            {shape.props.funnelName}
          </h3>

          {/* Funnel Stages */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {shape.props.stages.map((stage, i) => {
              const widthPercent = (stage.count / maxCount) * 100
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Stage Bar */}
                  <div
                    style={{
                      width: `${widthPercent}%`,
                      margin: '0 auto',
                      background: stage.color,
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px',
                      boxShadow: `0 4px 12px ${stage.color}40`,
                      transition: 'all 0.3s ease',
                      position: 'relative',
                      minHeight: '50px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.05)'
                      e.currentTarget.style.boxShadow = `0 6px 20px ${stage.color}60`
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)'
                      e.currentTarget.style.boxShadow = `0 4px 12px ${stage.color}40`
                    }}
                  >
                    <div style={{ textAlign: 'center', color: 'white' }}>
                      <div style={{ fontSize: '13px', fontWeight: 'bold' }}>
                        {stage.name}
                      </div>
                      {shape.props.showMetrics && (
                        <div style={{ fontSize: '11px', marginTop: '4px', opacity: 0.9 }}>
                          {stage.count.toLocaleString()} ({stage.conversionRate}%)
                        </div>
                      )}
                    </div>

                    {/* Drop-off indicator */}
                    {i > 0 && shape.props.showMetrics && (
                      <div
                        style={{
                          position: 'absolute',
                          right: '-24px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          fontSize: '16px',
                        }}
                      >
                        ↓
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Summary */}
          {shape.props.showMetrics && (
            <div
              style={{
                marginTop: '16px',
                padding: '12px',
                background: '#f3f4f6',
                borderRadius: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '11px',
                color: '#4b5563',
              }}
            >
              <div>
                <strong>Total Conversion:</strong>{' '}
                {((shape.props.stages[shape.props.stages.length - 1].count / shape.props.stages[0].count) * 100).toFixed(1)}%
              </div>
              <div>
                <strong>Final:</strong> {shape.props.stages[shape.props.stages.length - 1].count.toLocaleString()}
              </div>
            </div>
          )}
        </div>
      )
    }

    const renderModernFunnel = () => {
      return (
        <div
          style={{
            padding: '20px',
            height: '100%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '12px',
          }}
        >
          {/* Title */}
          <h3
            style={{
              fontSize: '20px',
              fontWeight: 'bold',
              color: 'white',
              marginBottom: '24px',
              textAlign: 'center',
              textShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            {shape.props.funnelName}
          </h3>

          {/* Funnel with Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {shape.props.stages.map((stage, i) => (
              <div
                key={i}
                style={{
                  background: 'rgba(255,255,255,0.95)',
                  borderRadius: '12px',
                  padding: '16px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                {/* Stage Number */}
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: stage.color,
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    fontSize: '14px',
                    flexShrink: 0,
                  }}
                >
                  {i + 1}
                </div>

                {/* Stage Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#1f2937' }}>
                    {stage.name}
                  </div>
                  {shape.props.showMetrics && (
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                      {stage.count.toLocaleString()} users • {stage.conversionRate}% conversion
                    </div>
                  )}
                </div>

                {/* Progress Bar */}
                <div
                  style={{
                    width: '60px',
                    height: '6px',
                    background: '#e5e7eb',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${(stage.count / maxCount) * 100}%`,
                      height: '100%',
                      background: stage.color,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    const renderMinimalFunnel = () => {
      return (
        <div style={{ padding: '24px', height: '100%', background: 'white' }}>
          {/* Title */}
          <h3
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#111827',
              marginBottom: '20px',
              borderBottom: '2px solid #e5e7eb',
              paddingBottom: '8px',
            }}
          >
            {shape.props.funnelName}
          </h3>

          {/* Simple List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {shape.props.stages.map((stage, i) => (
              <div key={i}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '6px',
                  }}
                >
                  <span style={{ fontSize: '13px', fontWeight: 500, color: '#374151' }}>
                    {stage.name}
                  </span>
                  {shape.props.showMetrics && (
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>
                      {stage.count.toLocaleString()}
                    </span>
                  )}
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '8px',
                    background: '#f3f4f6',
                    borderRadius: '4px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${(stage.count / maxCount) * 100}%`,
                      height: '100%',
                      background: stage.color,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
                {shape.props.showMetrics && i < shape.props.stages.length - 1 && (
                  <div style={{ fontSize: '10px', color: '#9ca3af', marginTop: '4px' }}>
                    ↓ {stage.conversionRate}% conversion to next stage
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )
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
            borderRadius: '12px',
            overflow: 'hidden',
            boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
            background: shape.props.style === 'modern' ? 'transparent' : 'white',
          }}
        >
          {shape.props.style === 'classic' && renderClassicFunnel()}
          {shape.props.style === 'modern' && renderModernFunnel()}
          {shape.props.style === 'minimal' && renderMinimalFunnel()}

          {/* Type Label */}
          <div
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              background: '#8b5cf6',
              color: 'white',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '10px',
              fontWeight: 'bold',
              boxShadow: '0 2px 8px rgba(139, 92, 246, 0.4)',
            }}
          >
            📊 Funnel
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: SalesFunnelNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
