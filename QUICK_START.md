# Quick Start Guide
## Get Started with 10x-Team Visualization Canvas in 5 Minutes

---

## ⚡ Quick Install & Start

### Step 1: Install Dependencies

```bash
# Install canvas dependencies
cd canvas
npm install

# Install upload server dependencies
cd server
npm install
cd ../..
```

### Step 2: Start Everything

```bash
# Terminal 1: Start the canvas (do this from the canvas directory)
cd canvas
npm run dev

# Terminal 2: Start upload server (do this from the canvas/server directory)
cd canvas/server
npm start
```

### Step 3: Open Canvas

Open your browser to: **http://localhost:3000**

---

## 🎨 Try These Examples

### Example 1: Create a Sales Funnel (2 minutes)

1. Open canvas at http://localhost:3000
2. Look for the **📈 Sales Funnel** button in the sidebar (or add via toolbar)
3. Click it to add a funnel node
4. The funnel appears with default data
5. Click the 💾 button (bottom-right) → **Export PNG**
6. Done! You have a professional sales funnel visualization

**What you see**: A beautiful conversion funnel with:
- 5 stages (Awareness → Interest → Consideration → Intent → Purchase)
- Conversion percentages
- Visual drop-off between stages
- Total conversion rate

### Example 2: Create a Presentation Slide (1 minute)

1. Click **📊 Presentation** in sidebar
2. A title slide appears
3. Double-click the title text to edit
4. Change to "My Product Launch"
5. Export as PNG
6. Done! Professional presentation slide

**Layouts available**:
- Title (hero slide)
- Content (with bullet points)
- Image + Text
- Full image
- Split view

### Example 3: Design a Landing Page (3 minutes)

1. Click **🎨 Landing Page** in sidebar
2. A full page mockup appears with:
   - Browser chrome
   - Navbar
   - Hero section
   - Content sections
   - Footer
3. Configure:
   - Change headline: "Transform Your Business"
   - Change CTA: "Start Free Trial"
   - Pick color scheme: Purple
4. Export as PNG
5. Done! Client-ready landing page mockup

### Example 4: Upload an Image (1 minute)

1. Click **🖼️ Image** in sidebar
2. Drag an image file onto the node OR click "Browse Files"
3. Image uploads to server
4. AI vision analysis (placeholder) activates
5. Add description and tags
6. Done! Image ready to use in workflows

**Supported formats**: JPG, PNG, GIF, WebP (up to 100MB)

### Example 5: Create a Data Chart (2 minutes)

1. Click **📊 Chart** in sidebar
2. A bar chart appears with sample data
3. Chart types available:
   - Bar chart (default)
   - Line chart
   - Pie chart
4. Change color scheme (Default, Vibrant, Pastel, Monochrome)
5. Export as PNG or SVG
6. Done! Chart ready for reports

---

## 💾 Export Your Work

Click the **💾 button** (bottom-right corner) for:

- **📸 PNG** - High-res image for sharing
- **🎨 SVG** - Vector graphic (editable)
- **📄 PDF** - Print-ready document
- **⚡ Workflow** - Executable JSON for Claude Code
- **📋 Clipboard** - Quick copy
- **💾 Save** - Save canvas as .10x file

---

## 🎯 Common Use Cases

### For Client Presentations
```
1. Add Presentation Slide (Title)
2. Add Presentation Slide (Features - bullet points)
3. Add Chart (metrics)
4. Add Presentation Slide (CTA)
5. Export all as PNG
6. Combine in PowerPoint or send directly
```

### For Landing Page Mockup
```
1. Add Landing Page node
2. Configure headline, CTA, sections
3. Choose color scheme
4. Export as PNG
5. Share with design team or client
```

### For Campaign Planning
```
1. Add Ad Campaign (Facebook)
2. Add Ad Campaign (Google)
3. Add Ad Campaign (LinkedIn)
4. Add Sales Funnel (show results)
5. Export Workflow JSON
6. Execute with Claude Code
```

### For Sales Reports
```
1. Add Sales Funnel (conversion data)
2. Add 2-3 Charts (revenue, growth, sources)
3. Arrange in grid
4. Export as PDF
5. Include in quarterly report
```

---

## 🔧 Troubleshooting

### Canvas won't start?
```bash
cd canvas
rm -rf node_modules
npm install
npm run dev
```

### Upload server error?
```bash
cd canvas/server
npm install
npm start
# Check: http://localhost:3002/api/upload/health
```

### Export not working?
- Try with fewer nodes
- Use SVG instead of PNG
- Check browser console for errors
- Clear browser cache

### Can't upload images?
- Verify upload server is running (port 3002)
- Check file size < 100MB
- Supported: JPG, PNG, GIF, WebP
- Try a different file

---

## 📚 Learn More

- **Full Guide**: See `CANVAS_VISUALIZATION_GUIDE.md`
- **Architecture**: See `CANVAS_AI_DESIGN.md`
- **Implementation**: See `PHASE1_IMPLEMENTATION_COMPLETE.md`

---

## 🎉 You're Ready!

**3 things to try right now**:

1. ✅ Create a sales funnel and export as PNG
2. ✅ Design a presentation slide with your headline
3. ✅ Build a landing page mockup for your product

**Time to create**: 5-10 minutes total
**Time saved**: 3-6 hours of manual work

---

**Need help?**
- Check the full guide: `CANVAS_VISUALIZATION_GUIDE.md`
- Review examples in the guide
- Check node files in `canvas/src/nodes/`

**Happy creating! 🚀**
