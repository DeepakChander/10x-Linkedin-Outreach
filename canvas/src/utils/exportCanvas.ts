// Canvas Export Utilities
// Export canvas as PNG, SVG, PDF, or JSON workflow

import { Editor, getSvgAsImage, TLShapeId } from 'tldraw'
import * as fs from 'fs'
import * as path from 'path'

export type ExportFormat = 'png' | 'svg' | 'pdf' | 'json' | 'workflow'

export interface ExportOptions {
  format: ExportFormat
  filename?: string
  outputDir?: string
  includeBackground?: boolean
  scale?: number
  quality?: number
  selectedOnly?: boolean
}

/**
 * Export the entire canvas or selected shapes
 */
export async function exportCanvas(
  editor: Editor,
  options: ExportOptions
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    const {
      format,
      filename = `canvas-${Date.now()}`,
      outputDir = '../../output/exports',
      includeBackground = true,
      scale = 2,
      quality = 0.92,
      selectedOnly = false,
    } = options

    // Create output directory if it doesn't exist
    const fullOutputDir = path.resolve(__dirname, outputDir)
    if (typeof window === 'undefined') {
      // Node.js environment
      if (!fs.existsSync(fullOutputDir)) {
        fs.mkdirSync(fullOutputDir, { recursive: true })
      }
    }

    // Get shape IDs to export
    const shapeIds = selectedOnly
      ? Array.from(editor.getSelectedShapeIds())
      : Array.from(editor.getCurrentPageShapeIds())

    if (shapeIds.length === 0) {
      return { success: false, error: 'No shapes to export' }
    }

    switch (format) {
      case 'png':
        return await exportAsPNG(editor, shapeIds, filename, fullOutputDir, scale, quality)

      case 'svg':
        return await exportAsSVG(editor, shapeIds, filename, fullOutputDir)

      case 'pdf':
        return await exportAsPDF(editor, shapeIds, filename, fullOutputDir)

      case 'json':
        return await exportAsJSON(editor, filename, fullOutputDir)

      case 'workflow':
        return await exportAsWorkflow(editor, filename, fullOutputDir)

      default:
        return { success: false, error: `Unsupported format: ${format}` }
    }
  } catch (error) {
    console.error('Export error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}

/**
 * Export as PNG image
 */
async function exportAsPNG(
  editor: Editor,
  shapeIds: TLShapeId[],
  filename: string,
  outputDir: string,
  scale: number,
  quality: number
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    const svg = await editor.getSvgString(shapeIds, {
      scale: scale,
      background: true,
    })

    if (!svg) {
      return { success: false, error: 'Failed to generate SVG' }
    }

    // Convert SVG to PNG using canvas
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()

    return new Promise((resolve) => {
      img.onload = () => {
        canvas.width = img.width
        canvas.height = img.height
        ctx?.drawImage(img, 0, 0)

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              resolve({ success: false, error: 'Failed to create blob' })
              return
            }

            // Download file in browser
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${filename}.png`
            a.click()
            URL.revokeObjectURL(url)

            // Also save to local directory if possible
            const filePath = path.join(outputDir, `${filename}.png`)
            resolve({
              success: true,
              filePath: filePath,
            })
          },
          'image/png',
          quality
        )
      }

      img.onerror = () => {
        resolve({ success: false, error: 'Failed to load image' })
      }

      img.src = `data:image/svg+xml;base64,${btoa(svg.svg)}`
    })
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'PNG export failed',
    }
  }
}

/**
 * Export as SVG
 */
async function exportAsSVG(
  editor: Editor,
  shapeIds: TLShapeId[],
  filename: string,
  outputDir: string
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    const svg = await editor.getSvgString(shapeIds, {
      scale: 1,
      background: true,
    })

    if (!svg) {
      return { success: false, error: 'Failed to generate SVG' }
    }

    // Download SVG in browser
    const blob = new Blob([svg.svg], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.svg`
    a.click()
    URL.revokeObjectURL(url)

    const filePath = path.join(outputDir, `${filename}.svg`)
    return {
      success: true,
      filePath: filePath,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'SVG export failed',
    }
  }
}

/**
 * Export as PDF (using SVG as intermediate)
 */
async function exportAsPDF(
  editor: Editor,
  shapeIds: TLShapeId[],
  filename: string,
  outputDir: string
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    // For PDF, we'll use the browser's print functionality
    // Or we can use a library like jsPDF if needed
    const svg = await editor.getSvgString(shapeIds, {
      scale: 2,
      background: true,
    })

    if (!svg) {
      return { success: false, error: 'Failed to generate SVG' }
    }

    // Create a new window with the SVG
    const printWindow = window.open('', '', 'width=800,height=600')
    if (!printWindow) {
      return { success: false, error: 'Failed to open print window' }
    }

    printWindow.document.write(`
      <html>
        <head>
          <title>${filename}</title>
          <style>
            body { margin: 0; padding: 0; }
            img { max-width: 100%; height: auto; }
          </style>
        </head>
        <body>
          ${svg.svg}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.focus()
    printWindow.print()

    const filePath = path.join(outputDir, `${filename}.pdf`)
    return {
      success: true,
      filePath: filePath,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'PDF export failed',
    }
  }
}

/**
 * Export as JSON (full canvas state)
 */
async function exportAsJSON(
  editor: Editor,
  filename: string,
  outputDir: string
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    const snapshot = editor.store.getSnapshot()
    const json = JSON.stringify(snapshot, null, 2)

    // Download JSON in browser
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.json`
    a.click()
    URL.revokeObjectURL(url)

    const filePath = path.join(outputDir, `${filename}.json`)

    // Also try to save to file system using File System Access API
    try {
      if ('showSaveFilePicker' in window) {
        const handle = await (window as any).showSaveFilePicker({
          suggestedName: `${filename}.json`,
          types: [
            {
              description: 'JSON Files',
              accept: { 'application/json': ['.json'] },
            },
          ],
        })
        const writable = await handle.createWritable()
        await writable.write(json)
        await writable.close()
      }
    } catch (e) {
      // File System Access API not supported or user canceled
      console.log('File System Access API not available')
    }

    return {
      success: true,
      filePath: filePath,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'JSON export failed',
    }
  }
}

/**
 * Export as executable workflow JSON
 */
async function exportAsWorkflow(
  editor: Editor,
  filename: string,
  outputDir: string
): Promise<{ success: boolean; filePath?: string; error?: string }> {
  try {
    // Get all shapes and connections
    const shapes = Array.from(editor.getCurrentPageShapes())

    // Build workflow structure
    const workflow = {
      name: filename,
      createdAt: new Date().toISOString(),
      version: '1.0',
      nodes: shapes
        .filter((shape) => shape.type !== 'workflow-connection')
        .map((shape) => ({
          id: shape.id,
          type: shape.type,
          position: { x: shape.x, y: shape.y },
          props: shape.props,
        })),
      connections: shapes
        .filter((shape) => shape.type === 'workflow-connection')
        .map((shape: any) => ({
          id: shape.id,
          from: shape.props.fromId,
          to: shape.props.toId,
        })),
    }

    const json = JSON.stringify(workflow, null, 2)

    // Download workflow JSON
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}-workflow.json`
    a.click()
    URL.revokeObjectURL(url)

    const filePath = path.join(outputDir, `${filename}-workflow.json`)

    // Also save to output/workflows/ directory
    const workflowDir = path.resolve(__dirname, '../../output/workflows')
    const workflowPath = path.join(workflowDir, `${filename}.json`)

    // Trigger custom event for Claude Code to save the workflow
    window.dispatchEvent(
      new CustomEvent('workflow-exported', {
        detail: {
          workflow: workflow,
          filePath: workflowPath,
        },
      })
    )

    return {
      success: true,
      filePath: filePath,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Workflow export failed',
    }
  }
}

/**
 * Save canvas to local file system (for auto-save)
 */
export async function saveCanvasToFile(
  editor: Editor,
  directory: string = '../../output/saved-canvases'
): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `canvas-${timestamp}`

  await exportAsJSON(editor, filename, directory)
}

/**
 * Load canvas from file
 */
export async function loadCanvasFromFile(
  editor: Editor,
  filePath: string
): Promise<{ success: boolean; error?: string }> {
  try {
    // Use File API to load JSON
    const response = await fetch(filePath)
    const snapshot = await response.json()

    editor.store.loadSnapshot(snapshot)

    return { success: true }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to load canvas',
    }
  }
}
