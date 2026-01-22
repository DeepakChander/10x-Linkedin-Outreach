import { BaseBoxShapeUtil, HTMLContainer, T, TLBaseShape } from 'tldraw'

// Chart node for data visualization
export type ChartNodeShape = TLBaseShape<
  'chart-node',
  {
    w: number
    h: number
    chartTitle: string
    chartType: 'bar' | 'line' | 'pie' | 'area' | 'donut'
    data: Array<{ label: string; value: number; color?: string }>
    showLegend: boolean
    showValues: boolean
    colorScheme: 'default' | 'vibrant' | 'pastel' | 'monochrome'
  }
>

export class ChartNodeShapeUtil extends BaseBoxShapeUtil<ChartNodeShape> {
  static override type = 'chart-node' as const

  static override props = {
    w: T.number,
    h: T.number,
    chartTitle: T.string,
    chartType: T.string,
    data: T.arrayOf(T.any),
    showLegend: T.boolean,
    showValues: T.boolean,
    colorScheme: T.string,
  }

  getDefaultProps(): ChartNodeShape['props'] {
    return {
      w: 420,
      h: 360,
      chartTitle: 'Monthly Revenue',
      chartType: 'bar',
      data: [
        { label: 'Jan', value: 4500 },
        { label: 'Feb', value: 5200 },
        { label: 'Mar', value: 6800 },
        { label: 'Apr', value: 5900 },
        { label: 'May', value: 7200 },
        { label: 'Jun', value: 8100 },
      ],
      showLegend: true,
      showValues: true,
      colorScheme: 'vibrant',
    }
  }

  component(shape: ChartNodeShape) {
    const colorSchemes = {
      default: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'],
      vibrant: ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#3b82f6', '#a855f7'],
      pastel: ['#fca5a5', '#fcd34d', '#a7f3d0', '#93c5fd', '#c4b5fd', '#f9a8d4'],
      monochrome: ['#1f2937', '#374151', '#4b5563', '#6b7280', '#9ca3af', '#d1d5db'],
    }

    const colors = colorSchemes[shape.props.colorScheme] || colorSchemes.default
    const maxValue = Math.max(...shape.props.data.map((d) => d.value))

    const renderBarChart = () => {
      return (
        <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Chart Area */}
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'flex-end',
              gap: '12px',
              padding: '20px 0',
            }}
          >
            {shape.props.data.map((item, i) => {
              const heightPercent = (item.value / maxValue) * 100
              const color = item.color || colors[i % colors.length]
              return (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  {/* Value Label */}
                  {shape.props.showValues && (
                    <div style={{ fontSize: '11px', fontWeight: 'bold', color: color }}>
                      {item.value.toLocaleString()}
                    </div>
                  )}
                  {/* Bar */}
                  <div
                    style={{
                      width: '100%',
                      height: `${heightPercent}%`,
                      background: color,
                      borderRadius: '6px 6px 0 0',
                      boxShadow: `0 4px 12px ${color}40`,
                      transition: 'all 0.3s ease',
                      minHeight: '20px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scaleY(1.05)'
                      e.currentTarget.style.filter = 'brightness(1.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scaleY(1)'
                      e.currentTarget.style.filter = 'brightness(1)'
                    }}
                  />
                  {/* Label */}
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: 500 }}>
                    {item.label}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )
    }

    const renderLineChart = () => {
      const width = 380
      const height = 200
      const padding = 30

      const xScale = (width - 2 * padding) / (shape.props.data.length - 1)
      const yScale = (height - 2 * padding) / maxValue

      const points = shape.props.data
        .map((item, i) => {
          const x = padding + i * xScale
          const y = height - padding - item.value * yScale
          return `${x},${y}`
        })
        .join(' ')

      return (
        <div style={{ padding: '16px' }}>
          <svg width={width} height={height} style={{ overflow: 'visible' }}>
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((fraction, i) => {
              const y = padding + fraction * (height - 2 * padding)
              return (
                <line
                  key={i}
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
              )
            })}

            {/* Line path */}
            <polyline
              points={points}
              fill="none"
              stroke={colors[0]}
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Area under line */}
            <polygon
              points={`${padding},${height - padding} ${points} ${width - padding},${height - padding}`}
              fill={`${colors[0]}30`}
            />

            {/* Data points */}
            {shape.props.data.map((item, i) => {
              const x = padding + i * xScale
              const y = height - padding - item.value * yScale
              return (
                <g key={i}>
                  <circle cx={x} cy={y} r="5" fill="white" stroke={colors[0]} strokeWidth="2" />
                  {shape.props.showValues && (
                    <text
                      x={x}
                      y={y - 12}
                      textAnchor="middle"
                      fontSize="10"
                      fontWeight="bold"
                      fill={colors[0]}
                    >
                      {item.value}
                    </text>
                  )}
                  <text
                    x={x}
                    y={height - padding + 20}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#6b7280"
                  >
                    {item.label}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      )
    }

    const renderPieChart = () => {
      const total = shape.props.data.reduce((sum, item) => sum + item.value, 0)
      const centerX = 150
      const centerY = 120
      const radius = 80

      let currentAngle = -90

      return (
        <div style={{ padding: '16px', display: 'flex', gap: '20px', alignItems: 'center' }}>
          {/* Pie Chart */}
          <svg width={300} height={240}>
            {shape.props.data.map((item, i) => {
              const percentage = (item.value / total) * 100
              const angle = (percentage / 100) * 360
              const color = item.color || colors[i % colors.length]

              const startAngle = currentAngle
              const endAngle = currentAngle + angle
              currentAngle = endAngle

              const startRad = (startAngle * Math.PI) / 180
              const endRad = (endAngle * Math.PI) / 180

              const x1 = centerX + radius * Math.cos(startRad)
              const y1 = centerY + radius * Math.sin(startRad)
              const x2 = centerX + radius * Math.cos(endRad)
              const y2 = centerY + radius * Math.sin(endRad)

              const largeArc = angle > 180 ? 1 : 0

              const pathData = [
                `M ${centerX} ${centerY}`,
                `L ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`,
                'Z',
              ].join(' ')

              // Calculate label position
              const midAngle = (startAngle + endAngle) / 2
              const midRad = (midAngle * Math.PI) / 180
              const labelX = centerX + (radius * 0.65) * Math.cos(midRad)
              const labelY = centerY + (radius * 0.65) * Math.sin(midRad)

              return (
                <g key={i}>
                  <path
                    d={pathData}
                    fill={color}
                    stroke="white"
                    strokeWidth="2"
                    style={{ transition: 'all 0.3s ease' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.filter = 'brightness(1.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.filter = 'brightness(1)'
                    }}
                  />
                  {percentage > 5 && (
                    <text
                      x={labelX}
                      y={labelY}
                      textAnchor="middle"
                      fontSize="12"
                      fontWeight="bold"
                      fill="white"
                    >
                      {percentage.toFixed(0)}%
                    </text>
                  )}
                </g>
              )
            })}
          </svg>

          {/* Legend */}
          {shape.props.showLegend && (
            <div style={{ flex: 1 }}>
              {shape.props.data.map((item, i) => {
                const color = item.color || colors[i % colors.length]
                const percentage = ((item.value / total) * 100).toFixed(1)
                return (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginBottom: '8px',
                    }}
                  >
                    <div
                      style={{
                        width: '16px',
                        height: '16px',
                        borderRadius: '4px',
                        background: color,
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: '#1f2937' }}>
                        {item.label}
                      </div>
                      <div style={{ fontSize: '10px', color: '#6b7280' }}>
                        {item.value.toLocaleString()} ({percentage}%)
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
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
            background: 'white',
            borderRadius: '12px',
            border: '2px solid #e5e7eb',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Title */}
          <div
            style={{
              padding: '16px',
              borderBottom: '2px solid #f3f4f6',
              background: '#fafafa',
            }}
          >
            <h3
              style={{
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#1f2937',
                margin: 0,
              }}
            >
              {shape.props.chartTitle}
            </h3>
            <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
              {shape.props.chartType.charAt(0).toUpperCase() + shape.props.chartType.slice(1)} Chart
            </div>
          </div>

          {/* Chart Content */}
          <div style={{ flex: 1, overflow: 'auto' }}>
            {shape.props.chartType === 'bar' && renderBarChart()}
            {shape.props.chartType === 'line' && renderLineChart()}
            {(shape.props.chartType === 'pie' || shape.props.chartType === 'donut') &&
              renderPieChart()}
          </div>

          {/* Type Badge */}
          <div
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              background: '#06b6d4',
              color: 'white',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '10px',
              fontWeight: 'bold',
              boxShadow: '0 2px 8px rgba(6, 182, 212, 0.4)',
            }}
          >
            📈 Chart
          </div>
        </div>
      </HTMLContainer>
    )
  }

  indicator(shape: ChartNodeShape) {
    return <rect width={shape.props.w} height={shape.props.h} rx={12} ry={12} />
  }
}
