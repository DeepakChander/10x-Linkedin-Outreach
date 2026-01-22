// File Upload Server for 10x-Team Canvas
// Handles image/video uploads and provides file serving
// Run with: node canvas/server/upload-server.js

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
const PORT = 3002;

// Enable CORS for canvas app
app.use(cors());
app.use(express.json());

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, '../../output/uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const hash = crypto.randomBytes(16).toString('hex');
    const ext = path.extname(file.originalname);
    cb(null, `${hash}${ext}`);
  },
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB max file size
  },
  fileFilter: (req, file, cb) => {
    // Allow images, videos, and PDFs
    const allowedTypes = /jpeg|jpg|png|gif|webp|mp4|mov|avi|mkv|pdf/;
    const ext = path.extname(file.originalname).toLowerCase().substring(1);
    const mimeType = file.mimetype.toLowerCase();

    if (allowedTypes.test(ext) || mimeType.startsWith('image/') || mimeType.startsWith('video/')) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only images, videos, and PDFs are allowed.'));
    }
  },
});

// Serve uploaded files statically
app.use('/uploads', express.static(uploadsDir));

// Health check endpoint
app.get('/api/upload/health', (req, res) => {
  res.json({ status: 'ok', service: 'upload-server', port: PORT });
});

// Single file upload endpoint
app.post('/api/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const fileUrl = `/uploads/${req.file.filename}`;
    const fullUrl = `http://localhost:${PORT}${fileUrl}`;

    res.json({
      success: true,
      file: {
        id: req.file.filename,
        name: req.file.originalname,
        size: req.file.size,
        type: req.file.mimetype,
        url: fileUrl,
        fullUrl: fullUrl,
        path: req.file.path,
      },
    });

    console.log(`✅ File uploaded: ${req.file.originalname} (${(req.file.size / 1024).toFixed(2)} KB)`);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Multiple files upload endpoint
app.post('/api/upload/multiple', upload.array('files', 10), (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const files = req.files.map((file) => ({
      id: file.filename,
      name: file.originalname,
      size: file.size,
      type: file.mimetype,
      url: `/uploads/${file.filename}`,
      fullUrl: `http://localhost:${PORT}/uploads/${file.filename}`,
      path: file.path,
    }));

    res.json({
      success: true,
      files: files,
      count: files.length,
    });

    console.log(`✅ ${files.length} files uploaded`);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Delete file endpoint
app.delete('/api/upload/:filename', (req, res) => {
  try {
    const filename = req.params.filename;
    const filePath = path.join(uploadsDir, filename);

    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`🗑️  File deleted: ${filename}`);
      res.json({ success: true, message: 'File deleted' });
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ error: error.message });
  }
});

// List uploaded files endpoint
app.get('/api/upload/list', (req, res) => {
  try {
    const files = fs.readdirSync(uploadsDir).map((filename) => {
      const filePath = path.join(uploadsDir, filename);
      const stats = fs.statSync(filePath);
      return {
        id: filename,
        name: filename,
        size: stats.size,
        url: `/uploads/${filename}`,
        fullUrl: `http://localhost:${PORT}/uploads/${filename}`,
        uploadedAt: stats.birthtime,
      };
    });

    res.json({
      success: true,
      files: files,
      count: files.length,
    });
  } catch (error) {
    console.error('List error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large. Maximum size is 100MB' });
    }
    return res.status(400).json({ error: error.message });
  }
  res.status(500).json({ error: error.message });
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║           10x-Team Canvas Upload Server                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Status: Running                                             ║
║  Port: ${PORT}                                                     ║
║  Uploads directory: ${uploadsDir}
║                                                              ║
║  Endpoints:                                                  ║
║  POST   /api/upload             - Upload single file        ║
║  POST   /api/upload/multiple    - Upload multiple files     ║
║  GET    /api/upload/list        - List all files            ║
║  DELETE /api/upload/:filename   - Delete a file             ║
║  GET    /uploads/:filename      - Serve uploaded file       ║
║                                                              ║
║  Supported formats:                                          ║
║  • Images: JPG, PNG, GIF, WebP                               ║
║  • Videos: MP4, MOV, AVI, MKV                                ║
║  • Documents: PDF                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, shutting down gracefully');
  process.exit(0);
});
