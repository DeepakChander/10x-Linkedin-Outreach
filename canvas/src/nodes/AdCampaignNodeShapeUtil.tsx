import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'

// Ad Campaign node for advertisement flow visualization
export type AdCampaignNodeShape = TLBaseShape<
  'ad-campaign-node',
  {
    w: number
    h: number
    campaignName: string
    platform: 'facebook' | 'google' | 'linkedin' | 'twitter' | 'instagram' | 'multi'
    objective: 'awareness' | 'traffic' | 'engagement' | 'leads' | 'conversions'
    budget: number
    duration: string
    targeting: string
    adCopy: string
    metrics: {
      impressions?: number
      clicks?: number
      ctr?: number
      conversions?: number
      cost?: number
    }
    status: 'draft' | 'active' | 'paused' | 'completed'
  }
>

export class AdCampaignNodeShapeUtil extends BaseBoxShapeUtil<AdCampaignNodeShape> {
  static override type = 'ad-campaign-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    campaignName: T.string,
    platform: T.string,
    objective: T.string,
    budget: T.number,
    duration: T.string,
    targeting: T.string,
    adCopy: T.string,
    metrics: T.any,
    status: T.string,
  }

  getDefaultProps(): AdCampaignNodeShape['props'] {
    return {
      w: 380,
      h: 520,
      campaignName: 'Product Launch Campaign',
      platform: 'multi',
      objective: 'conversions',
      budget: 5000,
      duration: '30 days',
      targeting: 'Tech professionals, 25-45, Interested in SaaS',
      adCopy: 'Transform your workflow with our revolutionary tool. Start free today!',
      metrics: {
        impressions: 125000,
        clicks: 3500,
        ctr: 2.8,
        conversions: 175,
        cost: 28.57,
      },
      status: 'draft',
    }
  }

  component(shape: AdCampaignNodeShape) {
    const platformConfig = {
      facebook: { color: '#1877f2', icon: 'f', label: 'Facebook Ads' },
      google: { color: '#4285f4', icon: 'G', label: 'Google Ads' },
      linkedin: { color: '#0077b5', icon: 'in', label: 'LinkedIn Ads' },
      twitter: { color: '#1da1f2', icon: '𝕏', label: 'X (Twitter) Ads' },
      instagram: { color: '#e4405f', icon: '📸', label: 'Instagram Ads' },
      multi: { color: '#8b5cf6', icon: '🌐', label: 'Multi-Platform' },
    }

    const objectiveConfig = {
      awareness: { icon: '👁️', label: 'Brand Awareness' },
      traffic: { icon: '🚀', label: 'Website Traffic' },
      engagement: { icon: '💬', label: 'Engagement' },
      leads: { icon: '🎯', label: 'Lead Generation' },
      conversions: { icon: '💰', label: 'Conversions' },
    }

    const statusConfig = {
      draft: { color: '#6b7280', label: 'Draft', icon: '📝' },
      active: { color: '#10b981', label: 'Active', icon: '▶️' },
      paused: { color: '#f59e0b', label: 'Paused', icon: '⏸️' },
      completed: { color: '#3b82f6', label: 'Completed', icon: '✅' },
    }

    const platform = platformConfig[shape.props.platform] || platformConfig.multi
    const objective = objectiveConfig[shape.props.objective] || objectiveConfig.conversions
    const status = statusConfig[shape.props.status] || statusConfig.draft

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
            border: `3px solid ${platform.color}`,
            boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <div
            style={{
              background: platform.color,
              color: 'white',
              padding: '16px',
              borderBottom: '2px solid rgba(0,0,0,0.1)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px',
                    fontWeight: 'bold',
                  }}
                >
                  {platform.icon}
                </div>
                <div>
                  <div style={{ fontSize: '11px', opacity: 0.9 }}>{platform.label}</div>
                  <div style={{ fontSize: '15px', fontWeight: 'bold', marginTop: '2px' }}>
                    {shape.props.campaignName}
                  </div>
                </div>
              </div>
              <div
                style={{
                  padding: '6px 12px',
                  background: status.color,
                  borderRadius: '20px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <span>{status.icon}</span>
                <span>{status.label}</span>
              </div>
            </div>
          </div>

          {/* Campaign Details */}
          <div style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
            {/* Objective */}
            <div style={{ marginBottom: '16px' }}>
              <div
                style={{
                  fontSize: '11px',
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Campaign Objective
              </div>
              <div
                style={{
                  padding: '10px',
                  background: '#f3f4f6',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span style={{ fontSize: '18px' }}>{objective.icon}</span>
                <span style={{ fontSize: '13px', fontWeight: 600, color: '#1f2937' }}>
                  {objective.label}
                </span>
              </div>
            </div>

            {/* Budget & Duration */}
            <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    textTransform: 'uppercase',
                    fontWeight: 600,
                    marginBottom: '6px',
                  }}
                >
                  Budget
                </div>
                <div
                  style={{
                    padding: '10px',
                    background: '#ecfdf5',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: '#059669',
                  }}
                >
                  ${shape.props.budget.toLocaleString()}
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    textTransform: 'uppercase',
                    fontWeight: 600,
                    marginBottom: '6px',
                  }}
                >
                  Duration
                </div>
                <div
                  style={{
                    padding: '10px',
                    background: '#eff6ff',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#1e40af',
                  }}
                >
                  {shape.props.duration}
                </div>
              </div>
            </div>

            {/* Targeting */}
            <div style={{ marginBottom: '16px' }}>
              <div
                style={{
                  fontSize: '11px',
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Targeting
              </div>
              <div
                style={{
                  padding: '10px',
                  background: '#fef3c7',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#92400e',
                  lineHeight: '1.5',
                }}
              >
                {shape.props.targeting}
              </div>
            </div>

            {/* Ad Copy */}
            <div style={{ marginBottom: '16px' }}>
              <div
                style={{
                  fontSize: '11px',
                  color: '#6b7280',
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  marginBottom: '6px',
                }}
              >
                Ad Copy
              </div>
              <div
                style={{
                  padding: '10px',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#374151',
                  lineHeight: '1.5',
                  fontStyle: 'italic',
                }}
              >
                "{shape.props.adCopy}"
              </div>
            </div>

            {/* Metrics */}
            {Object.keys(shape.props.metrics).length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: '11px',
                    color: '#6b7280',
                    textTransform: 'uppercase',
                    fontWeight: 600,
                    marginBottom: '10px',
                  }}
                >
                  Performance Metrics
                </div>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '8px',
                  }}
                >
                  {shape.props.metrics.impressions && (
                    <MetricCard
                      label="Impressions"
                      value={shape.props.metrics.impressions.toLocaleString()}
                      icon="👁️"
                      color="#3b82f6"
                    />
                  )}
                  {shape.props.metrics.clicks && (
                    <MetricCard
                      label="Clicks"
                      value={shape.props.metrics.clicks.toLocaleString()}
                      icon="🖱️"
                      color="#8b5cf6"
                    />
                  )}
                  {shape.props.metrics.ctr && (
                    <MetricCard
                      label="CTR"
                      value={`${shape.props.metrics.ctr}%`}
                      icon="📊"
                      color="#10b981"
                    />
                  )}
                  {shape.props.metrics.conversions && (
                    <MetricCard
                      label="Conversions"
                      value={shape.props.metrics.conversions.toLocaleString()}
                      icon="✅"
                      color="#f59e0b"
                    />
                  )}
                  {shape.props.metrics.cost && (
                    <MetricCard
                      label="Cost/Conv"
                      value={`$${shape.props.metrics.cost}`}
                      icon="💵"
                      color="#ef4444"
                    />
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Type Badge */}
          <div
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              background: '#ec4899',
              color: 'white',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '10px',
              fontWeight: 'bold',
              boxShadow: '0 2px 8px rgba(236, 72, 153, 0.4)',
            }}
          >
            📢 Ad Campaign
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: AdCampaignNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}

// Helper component for metric cards
function MetricCard({
  label,
  value,
  icon,
  color,
}: {
  label: string
  value: string
  icon: string
  color: string
}) {
  return (
    <div
      style={{
        padding: '8px',
        background: 'white',
        border: `2px solid ${color}`,
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
      }}
    >
      <div style={{ fontSize: '10px', color: '#6b7280', fontWeight: 600 }}>
        <span style={{ marginRight: '4px' }}>{icon}</span>
        {label}
      </div>
      <div style={{ fontSize: '14px', fontWeight: 'bold', color: color }}>
        {value}
      </div>
    </div>
  )
}
