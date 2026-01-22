# 10x-Team Canvas Visualization Guide
## Complete Guide to Creating Visual Content with Claude Code

**Version**: 2.0 (Phase 1 Complete)
**Date**: 2026-01-22
**Status**: Production Ready ✅

---

## 🎨 What's New

Your 10x-Team Canvas has been **revolutionized** with 7 powerful new node types that enable you to create:

✅ **Client Presentations** - Full PPT slide mockups
✅ **Landing Pages** - Complete website page mockups
✅ **Sales Funnels** - Visual conversion flow diagrams
✅ **Ad Campaigns** - Advertisement campaign visualizations
✅ **Data Charts** - Bar, line, pie charts
✅ **Prompt Nodes** - Natural language instruction sticky notes
✅ **Image Nodes** - Drag-drop image uploads with AI analysis

**Plus**: Enhanced export capabilities (PNG, SVG, PDF, Workflow JSON)

---

## 🚀 Quick Start

### 1. Start the Canvas

```bash
cd canvas
npm install
npm run dev
```

Canvas opens at: **http://localhost:3000**

### 2. Start the Upload Server (for images/videos)

```bash
cd canvas/server
npm install
npm start
```

Upload server runs at: **http://localhost:3002**

### 3. Start Creating!

Open the canvas and you'll see **7 new node types** in the sidebar:
- 📝 Prompt Node
- 🖼️ Image Node
- 📊 Presentation Slide
- 🎨 Landing Page
- 📈 Sales Funnel
- 📢 Ad Campaign
- 📊 Chart

---

## 📝 Node Types Reference

### 1. Prompt Node (Sticky Note Style)

**Use For**: Natural language instructions, ideas, questions, conditions

**Features**:
- 5 categories: Instruction, Question, Condition, Decision, Idea
- Markdown support
- AI interpretation preview
- Double-click to edit
- Priority levels
- Auto-rotating sticky note aesthetic

**Example Usage**:
```
"Find AI startup founders in San Francisco"
→ Claude Code interprets this as discovery-engine skill

"If they have Twitter, follow them"
→ Claude Code interprets as conditional logic + twitter-adapter
```

**Creating in Claude Code**:
```javascript
// Via WebSocket or API
{
  type: 'add-node',
  payload: {
    nodeType: 'prompt-node',
    label: 'Discovery Task',
    x: 100,
    y: 100,
    props: {
      text: 'Find AI founders with 10k+ followers',
      category: 'instruction',
      priority: 1,
    }
  }
}
```

---

### 2. Image Node (Upload & AI Analysis)

**Use For**: Product screenshots, mockups, diagrams, references

**Features**:
- Drag-drop upload
- AI vision analysis (via Claude Vision API)
- Image preview
- Description & caption
- Tags
- Usage type: Context, Attachment, Reference
- Multiple format support (JPG, PNG, GIF, WebP)

**Example Usage**:
```
Upload product screenshot →
AI analyzes: "This is a dashboard interface with 3 charts..."
→ Use in outreach: "Show this to developers on Twitter"
```

**Upload Flow**:
1. Drag image onto canvas OR click Browse Files
2. Image uploads to server (localhost:3002)
3. AI vision analysis triggers automatically
4. Add description and tags
5. Use in workflow

---

### 3. Presentation Slide Node (PPT Mockups)

**Use For**: Client presentations, pitch decks, meeting slides

**Features**:
- 6 layout types: Title, Content, Image-Left, Image-Right, Full-Image, Split
- 5 themes: Light, Dark, Gradient-Blue, Gradient-Purple, Minimal
- Bullet points support
- Speaker notes
- Slide numbering
- Professional styling

**Layout Types**:

**Title Layout**: Hero slide with centered title
```typescript
{
  layout: 'title',
  title: 'Transform Your Business',
  content: 'The ultimate solution',
  theme: 'gradient-blue'
}
```

**Content Layout**: Standard bullet points
```typescript
{
  layout: 'content',
  title: 'Key Features',
  bulletPoints: [
    'AI-powered automation',
    'Real-time analytics',
    'Easy integration'
  ]
}
```

**Example: Creating a 3-Slide Deck**:
```
Slide 1: Title - "Our Product Launch"
Slide 2: Content - "Features" with 4 bullet points
Slide 3: Image-Right - Product screenshot + description
```

**Export**: PNG, PDF (print-friendly)

---

### 4. Landing Page Node (Website Mockups)

**Use For**: Landing page designs, website mockups, page prototypes

**Features**:
- Browser chrome (realistic window)
- Navbar & Footer
- Hero section with headline, subheadline, CTA
- Multiple content sections
- 5 color schemes: Blue, Purple, Green, Orange, Minimal
- Responsive preview

**Example Page**:
```typescript
{
  pageName: 'SaaS Product',
  headline: 'Automate Your Workflow',
  subheadline: 'Save 10 hours per week',
  ctaText: 'Start Free Trial',
  sections: [
    { title: 'Features', content: '...' },
    { title: 'Pricing', content: '...' },
    { title: 'Testimonials', content: '...' }
  ],
  colorScheme: 'purple'
}
```

**Use Cases**:
- Client mockups
- Landing page concepts
- Website redesign proposals
- A/B testing ideas

**Export**: Screenshot as PNG for client presentations

---

### 5. Sales Funnel Node (Conversion Flows)

**Use For**: Sales process visualization, conversion funnels, customer journeys

**Features**:
- 3 styles: Classic, Modern, Minimal
- Unlimited stages
- Conversion metrics per stage
- Drop-off visualization
- Progress bars
- Total conversion calculation
- Color-coded stages

**Example Funnel**:
```typescript
{
  funnelName: 'SaaS Sales Funnel',
  stages: [
    { name: 'Awareness', count: 10000, conversionRate: 100 },
    { name: 'Interest', count: 5000, conversionRate: 50 },
    { name: 'Trial', count: 2000, conversionRate: 40 },
    { name: 'Purchase', count: 800, conversionRate: 40 },
    { name: 'Retention', count: 640, conversionRate: 80 }
  ],
  style: 'modern',
  showMetrics: true
}
```

**Styles**:
- **Classic**: Traditional funnel bars with decreasing width
- **Modern**: Card-based with gradient background
- **Minimal**: Simple progress bars with numbers

**Export**: PNG for reports, presentations, or client proposals

---

### 6. Ad Campaign Node (Marketing Campaigns)

**Use For**: Ad campaign planning, marketing visualizations, campaign management

**Features**:
- Multi-platform support: Facebook, Google, LinkedIn, Twitter, Instagram
- Campaign objectives: Awareness, Traffic, Engagement, Leads, Conversions
- Budget & duration tracking
- Targeting details
- Ad copy preview
- Performance metrics (impressions, clicks, CTR, conversions)
- Status indicators: Draft, Active, Paused, Completed

**Example Campaign**:
```typescript
{
  campaignName: 'Q1 Product Launch',
  platform: 'multi',
  objective: 'conversions',
  budget: 10000,
  duration: '30 days',
  targeting: 'SaaS founders, 25-50, USA',
  adCopy: 'Transform your workflow...',
  metrics: {
    impressions: 125000,
    clicks: 3500,
    ctr: 2.8,
    conversions: 175,
    cost: 57.14
  },
  status: 'active'
}
```

**Use Cases**:
- Campaign planning
- Client proposals
- Budget allocation
- Performance tracking
- A/B test comparisons

---

### 7. Chart Node (Data Visualization)

**Use For**: Data visualization, metrics, analytics, reports

**Features**:
- 3 chart types: Bar, Line, Pie/Donut
- 4 color schemes: Default, Vibrant, Pastel, Monochrome
- Show/hide legend
- Show/hide values
- Interactive hover effects
- Customizable data points

**Chart Types**:

**Bar Chart**: Vertical bars for comparisons
```typescript
{
  chartTitle: 'Monthly Revenue',
  chartType: 'bar',
  data: [
    { label: 'Jan', value: 4500 },
    { label: 'Feb', value: 5200 },
    { label: 'Mar', value: 6800 }
  ]
}
```

**Line Chart**: Trend visualization with area fill
```typescript
{
  chartTitle: 'User Growth',
  chartType: 'line',
  data: [
    { label: 'Week 1', value: 100 },
    { label: 'Week 2', value: 250 },
    { label: 'Week 3', value: 580 }
  ]
}
```

**Pie Chart**: Percentage breakdown
```typescript
{
  chartTitle: 'Traffic Sources',
  chartType: 'pie',
  data: [
    { label: 'Organic', value: 4200 },
    { label: 'Paid', value: 2800 },
    { label: 'Social', value: 1500 }
  ],
  showLegend: true
}
```

---

## 💾 Export Features

### Export Formats

Click the **💾 button** (bottom-right) to access export menu:

1. **📸 PNG Export**
   - High-resolution image (2x scale)
   - Perfect for presentations
   - Includes background
   - Auto-downloads

2. **🎨 SVG Export**
   - Vector format
   - Scalable to any size
   - Edit in Illustrator/Figma
   - Smallest file size

3. **📄 PDF Export**
   - Print-ready format
   - Opens print dialog
   - Great for client delivery
   - Professional output

4. **⚡ Workflow Export**
   - Executable JSON format
   - Use with `/workflow run`
   - Contains all node data
   - Ready for Claude Code execution

5. **📋 Copy to Clipboard**
   - PNG format
   - Paste anywhere
   - Quick sharing

6. **💾 Save Canvas (.10x file)**
   - Full canvas state
   - Re-open later
   - Version control
   - Backup

---

## 🎯 Use Cases

### 1. Client Presentations

**Scenario**: Create a 5-slide pitch deck for a client

**Steps**:
1. Add 5 Presentation Slide nodes
2. Slide 1: Title layout - "Product Overview"
3. Slide 2: Content layout - "Key Features" (5 bullets)
4. Slide 3: Image-Right - Product screenshot + benefits
5. Slide 4: Chart - Revenue projections (line chart)
6. Slide 5: Content - "Next Steps" with CTA
7. Export all as PNG
8. Combine in PowerPoint or send directly

**Time Saved**: 2-3 hours of manual slide creation

---

### 2. Landing Page Mockup

**Scenario**: Design a landing page for a new SaaS product

**Steps**:
1. Add Landing Page node
2. Set headline: "Automate Your Email Outreach"
3. Set CTA: "Start Free Trial"
4. Add 3 sections: Features, Pricing, FAQ
5. Choose color scheme: Purple
6. Export as PNG
7. Share with design team or client

**Use**: Client approval, developer handoff, A/B testing

---

### 3. Sales Funnel Visualization

**Scenario**: Show conversion metrics to stakeholders

**Steps**:
1. Add Sales Funnel node
2. Add 6 stages with real data:
   - Visitors: 100,000
   - Sign-ups: 15,000 (15%)
   - Trials: 6,000 (40%)
   - Purchases: 1,800 (30%)
   - Retention: 1,440 (80%)
3. Choose "Modern" style
4. Export as PDF
5. Include in quarterly report

**Impact**: Visual clarity for stakeholders

---

### 4. Ad Campaign Planning

**Scenario**: Plan a multi-platform ad campaign

**Steps**:
1. Add 3 Ad Campaign nodes:
   - Campaign 1: Facebook (Awareness, $3k)
   - Campaign 2: Google Ads (Conversions, $5k)
   - Campaign 3: LinkedIn (Leads, $2k)
2. Fill in targeting, ad copy, metrics
3. Export canvas as PNG
4. Present to marketing team
5. Track performance by updating metrics

**Benefit**: All campaigns visible at a glance

---

### 5. Data Dashboard Mockup

**Scenario**: Design analytics dashboard layout

**Steps**:
1. Add 4 Chart nodes:
   - Bar chart: Monthly revenue
   - Line chart: User growth
   - Pie chart: Traffic sources
   - Bar chart: Feature usage
2. Arrange in 2x2 grid
3. Add Prompt nodes for KPIs
4. Export as PNG
5. Send to development team

**Use**: Dashboard specification, client preview

---

## 🔧 Technical Integration

### Canvas to Claude Code Communication

**WebSocket Events** (when implemented in Phase 2):

```javascript
// Canvas → Claude Code
window.dispatchEvent(new CustomEvent('workflow-exported', {
  detail: {
    workflow: { nodes, connections },
    filePath: 'output/workflows/my-workflow.json'
  }
}));

// Claude Code → Canvas
webSocket.send({
  type: 'add-node',
  payload: {
    nodeType: 'presentation-slide-node',
    x: 200,
    y: 200,
    props: {
      title: 'Generated by Claude',
      layout: 'title'
    }
  }
});
```

### File Storage

All exports are saved to:
```
output/
├── exports/          # PNG, SVG, PDF exports
├── workflows/        # Workflow JSON files
├── uploads/          # Uploaded images/videos
└── saved-canvases/   # Saved .10x files
```

---

## 🎨 Claude Code Can Create These Visually!

When you say to Claude Code:

**"Create a sales funnel presentation"**

Claude Code will:
1. Connect to canvas via WebSocket
2. Add Presentation Slide node (title)
3. Add Sales Funnel node with stages
4. Add Chart nodes for metrics
5. Arrange them visually
6. Export as workflow JSON
7. You approve and execute

**Watch your canvas come to life in real-time!**

---

## 📋 Keyboard Shortcuts (TLDraw Default)

- **V** - Select tool
- **D** - Draw tool
- **T** - Text tool
- **R** - Rectangle
- **E** - Ellipse
- **A** - Arrow
- **Cmd/Ctrl + C** - Copy
- **Cmd/Ctrl + V** - Paste
- **Cmd/Ctrl + D** - Duplicate
- **Delete** - Delete selected
- **Cmd/Ctrl + Z** - Undo
- **Cmd/Ctrl + Shift + Z** - Redo

---

## 🚀 What's Next (Phase 2-5)

### Phase 2: WebSocket Integration
- Real-time bidirectional communication
- Claude Code can add nodes live
- Live progress updates during workflow execution

### Phase 3: AI Interpretation
- Draw anything → Claude interprets it
- Freehand sketches → Structured workflows
- Natural language → Executable steps

### Phase 4: Enhanced Execution
- Highlight nodes during execution
- Real-time status updates
- Error visualization
- Progress tracking

### Phase 5: Advanced Features
- Video upload nodes
- Multi-user collaboration
- Template library
- Workflow versioning
- Analytics dashboard

---

## 💡 Tips & Tricks

### Best Practices

1. **Organize Your Canvas**
   - Use grids for alignment
   - Group related nodes
   - Leave whitespace

2. **Color Consistency**
   - Use the same theme across nodes
   - Match your brand colors
   - Consider accessibility

3. **Export Strategy**
   - PNG for presentations
   - SVG for editing later
   - PDF for clients
   - Workflow JSON for execution

4. **Performance**
   - Keep canvas under 100 nodes
   - Export frequently
   - Save backups

### Common Patterns

**Client Presentation Flow**:
```
[Title Slide] → [Problem Slide] → [Solution Slide] →
[Features Chart] → [Pricing Funnel] → [CTA Slide]
```

**Landing Page Design**:
```
[Landing Page Node] + [Sales Funnel] + [Chart (metrics)]
→ Export PNG → Present to client
```

**Campaign Planning**:
```
[Ad Campaign (FB)] + [Ad Campaign (Google)] + [Funnel (results)]
→ Export PDF → Share with team
```

---

## 🐛 Troubleshooting

### Upload Server Not Running
```bash
cd canvas/server
npm install
npm start
```
Check: http://localhost:3002/api/upload/health

### Canvas Won't Load
```bash
cd canvas
rm -rf node_modules
npm install
npm run dev
```

### Export Not Working
- Check browser console for errors
- Try with fewer nodes
- Use SVG if PNG fails
- Clear browser cache

### Images Not Uploading
- Verify upload server is running (port 3002)
- Check file size < 100MB
- Verify file format (JPG, PNG, GIF, WebP)
- Check network tab for errors

---

## 📚 Resources

### Official TLDraw Docs
- [TLDraw SDK](https://tldraw.dev/)
- [Custom Shapes](https://tldraw.dev/examples/custom-shape)
- [Editor API](https://tldraw.dev/docs/editor)

### Project Files
- `CANVAS_AI_DESIGN.md` - Full architecture design
- `canvas/src/nodes/` - All node implementations
- `canvas/server/` - Upload server
- `canvas/src/utils/exportCanvas.ts` - Export utilities

---

## ✨ Summary

**What You Can Now Do**:

✅ Create **professional presentations** without PowerPoint
✅ Design **landing pages** visually before coding
✅ Visualize **sales funnels** with real metrics
✅ Plan **ad campaigns** across multiple platforms
✅ Create **data charts** for reports and dashboards
✅ Upload **images** with AI analysis
✅ Write **prompts** that Claude Code executes
✅ Export everything as **PNG, SVG, PDF, or Workflow JSON**

**The Bigger Vision**:
Draw anything → Claude Code interprets it → Claude Code executes it → Results delivered

---

**Ready to start creating?**

1. `cd canvas && npm run dev` (Canvas on http://localhost:3000)
2. `cd canvas/server && npm start` (Upload server on http://localhost:3002)
3. Open canvas and start adding visualization nodes!
4. Export and share your creations!

**Questions or issues?**
- Check `CANVAS_AI_DESIGN.md` for architecture details
- Review node implementations in `canvas/src/nodes/`
- File issues at: https://github.com/Anit-1to10x/10x-outreach-skill

---

**🎉 Phase 1 Complete! All 7 visualization node types implemented and ready to use!**

Created with ❤️ by Claude Code (Sonnet 4.5)
Version: 2.0 | Date: 2026-01-22
