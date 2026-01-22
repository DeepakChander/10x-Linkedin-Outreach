# 🎥 Advanced Video Processing Guide

Complete guide for processing videos, transcripts, and social media content with Claude Code.

## 🚀 Features

### Video Processing Capabilities

1. **Video Upload & Analysis**
   - Drag & drop video files (MP4, WebM, MOV)
   - Automatic thumbnail generation
   - Duration detection
   - Video metadata extraction

2. **AI-Powered Transcription**
   - Whisper-based speech-to-text
   - Timestamp precision to the millisecond
   - Speaker diarization (who spoke when)
   - Multiple language support
   - Cloud API (AssemblyAI) or local Whisper

3. **Intelligent Clip Splitting**
   - Scene detection using FFmpeg
   - Automatic clip generation
   - Smart scene boundary detection
   - Customizable clip duration
   - Fallback 30-second chunks

4. **Comprehensive Summaries**
   - Full transcript with timestamps
   - Key points extraction
   - Timeline of topics discussed
   - Speaker analysis (total time, segments)
   - Action items extraction
   - Who spoke when, what they said

5. **URL Processing**
   - YouTube video download & processing
   - LinkedIn post content extraction
   - Instagram post data (via Browser-Use MCP)
   - Reddit post and comments extraction
   - Image fetching from social media
   - Metadata extraction

## 📦 Installation

### Step 1: Install FFmpeg

**Required** for video processing:

**Windows (with Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (Manual):**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### Step 2: Install Python Dependencies

```bash
# Install video processing dependencies
pip install -r requirements-video.txt
```

### Step 3: Optional - AssemblyAI API (Recommended)

For better transcription with speaker diarization:

1. Sign up at https://www.assemblyai.com/
2. Get your API key
3. Add to `.env`:

```env
ASSEMBLYAI_API_KEY=your_api_key_here
```

**Benefits:**
- Superior accuracy
- Speaker diarization (identifies who spoke when)
- Faster processing
- Auto-highlights
- Confidence scores

**Without API key:**
- Falls back to local Whisper (slower but free)
- No speaker diarization
- Requires more RAM

## 🎬 Usage Guide

### Method 1: Via Canvas UI

1. **Start the servers:**
   ```bash
   # Terminal 1: WebSocket Server
   cd canvas && npm run server

   # Terminal 2: Canvas UI
   cd canvas && npm run dev
   ```

2. **Open Canvas:**
   - Navigate to http://localhost:5175/

3. **Add Video Node:**
   - Click the 🎥 Video button in toolbar
   - Or drag from toolbar to canvas

4. **Upload Video:**
   - **Option A**: Drag & drop video file
   - **Option B**: Click "Browse Files"
   - **Option C**: Paste URL (YouTube, LinkedIn, etc.)

5. **Process URL:**
   - Paste URL in input field
   - Click "🚀 Process" button
   - Wait for processing (shows ⏳)
   - Results appear automatically

6. **View Results:**
   - Click "📝 Show Transcript" for full transcript
   - Click "✂️ X Clips" to see video clips
   - Click "Show AI Analysis" for summary
   - All data saved to `output/videos/`

### Method 2: Via Python Script

```bash
cd .claude/scripts

# Process local video
python video_processor.py process path/to/video.mp4

# Process YouTube video
python video_processor.py youtube "https://youtube.com/watch?v=..."

# Process any URL
python video_processor.py url "https://linkedin.com/posts/..."
```

### Method 3: Via Claude Code

Talk to Claude naturally:

```
You: "Process this YouTube video and give me a summary: https://youtube.com/watch?v=..."

Claude: [Processes video, extracts transcript, generates summary]
```

## 📊 Output Structure

All processed videos are saved to `output/videos/`:

```
output/videos/
├── clips/                      # Video clips
│   ├── video_clip_001.mp4
│   ├── video_clip_002.mp4
│   └── video_clip_003.mp4
│
├── transcripts/                # Transcription results
│   └── video_analysis.json    # Complete analysis
│
├── thumbnails/                 # Video thumbnails
│   └── video_thumb.jpg
│
└── youtube_abc123.mp4          # Downloaded videos
```

### Analysis JSON Structure

```json
{
  "video_path": "path/to/video.mp4",
  "duration": 180.5,
  "thumbnail": "path/to/thumbnail.jpg",

  "transcript": {
    "text": "Full transcript text...",
    "segments": [
      {
        "start": 0.0,
        "end": 5.2,
        "text": "Hello everyone...",
        "speaker": "Speaker 1"
      }
    ],
    "speakers": ["Speaker 1", "Speaker 2"],
    "language": "en",
    "confidence": 0.95
  },

  "clips": [
    {
      "clip_number": 1,
      "start_time": 0.0,
      "end_time": 30.0,
      "duration": 30.0,
      "path": "clips/video_clip_001.mp4"
    }
  ],

  "summary": {
    "full_transcript": "[00:00] Speaker 1: Hello...",

    "key_points": [
      {
        "timestamp": "00:15",
        "point": "Discussion about AI capabilities..."
      }
    ],

    "timeline": [
      {
        "start": "00:00",
        "end": "02:30",
        "topic": "Introduction and overview"
      }
    ],

    "speakers_summary": {
      "Speaker 1": {
        "total_time": 120.5,
        "total_time_formatted": "02:00",
        "segments": 15,
        "first_appearance": "00:00"
      }
    },

    "action_items": [
      "Follow up on AI integration",
      "Schedule next meeting"
    ]
  }
}
```

## 🌐 Supported URL Types

### YouTube

**Supported formats:**
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`

**What gets extracted:**
- Full video download
- Automatic transcription
- Clip generation
- Summary with timestamps
- Speaker identification
- Action items

**Example:**
```python
python video_processor.py youtube "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### LinkedIn

**Supported formats:**
- `https://linkedin.com/posts/username_activity...`
- `https://linkedin.com/feed/update/...`

**What gets extracted:**
- Post text content
- Author information
- Engagement metrics
- Images (basic)

**Note:** Full LinkedIn scraping requires authentication. Use `linkedin_adapter.py` with Browser-Use MCP for complete access.

**Example:**
```python
python video_processor.py url "https://linkedin.com/posts/..."
```

### Instagram

**Supported formats:**
- `https://instagram.com/p/POST_ID/`
- `https://instagram.com/reel/REEL_ID/`

**What gets extracted:**
- Basic post metadata

**Note:** Instagram requires authentication. Use `instagram_adapter.py` with Browser-Use MCP for:
- Full image/video download
- Comments
- Captions
- Engagement data

**Example:**
```python
# Via adapter (recommended)
python instagram_adapter.py fetch-post "https://instagram.com/p/..."
```

### Reddit

**Supported formats:**
- `https://reddit.com/r/subreddit/comments/POST_ID/...`
- `https://redd.it/POST_ID`

**What gets extracted:**
- Post title and text
- Author information
- Score and comments count
- Subreddit
- Creation timestamp
- Full comments (via API)

**Example:**
```python
python video_processor.py url "https://reddit.com/r/programming/comments/..."
```

## 🎯 Use Cases

### 1. Meeting Transcription

```bash
# Record your Zoom meeting, then:
python video_processor.py process meeting.mp4
```

**Output:**
- Full transcript with timestamps
- Who spoke when
- Key decisions made
- Action items
- Meeting summary

### 2. YouTube Course Processing

```bash
# Process educational video
python video_processor.py youtube "https://youtube.com/watch?v=..."
```

**Output:**
- Split into topic-based clips
- Searchable transcript
- Timeline of topics
- Key concepts highlighted

### 3. Social Media Content Analysis

```bash
# Analyze competitor LinkedIn posts
python video_processor.py url "https://linkedin.com/posts/competitor_..."
```

**Output:**
- Post content
- Engagement patterns
- Content themes
- Images for reference

### 4. Podcast Episode Analysis

```bash
# Process podcast video
python video_processor.py process podcast_ep5.mp4
```

**Output:**
- Speaker segments
- Topic timeline
- Quotable moments
- Show notes generation

## ⚙️ Configuration Options

### Local vs Cloud Processing

**Local Whisper (Default without API key):**
- Pros: Free, private, works offline
- Cons: Slower, no speaker IDs, high RAM usage

**AssemblyAI (With API key):**
- Pros: Fast, speaker diarization, high accuracy
- Cons: Costs money, requires internet

### Scene Detection Threshold

Adjust in `video_processor.py`:

```python
# More sensitive (more clips)
scenes = self._detect_scenes(video_path, threshold=0.2)

# Less sensitive (fewer clips)
scenes = self._detect_scenes(video_path, threshold=0.5)
```

### Clip Duration Fallback

If scene detection fails, clips default to 30 seconds.

Change in `_detect_scenes()`:

```python
chunk_duration = 60  # 60-second chunks instead of 30
```

## 🐛 Troubleshooting

### FFmpeg Not Found

```
Error: ffmpeg not found
```

**Solution:**
1. Install FFmpeg (see Installation)
2. Verify: `ffmpeg -version`
3. Restart terminal/IDE

### Whisper Out of Memory

```
Error: CUDA out of memory
```

**Solution:**
Use smaller Whisper model:

```python
model = whisper.load_model("tiny")  # Instead of "base"
```

### YouTube Download Fails

```
Error: Unable to extract video
```

**Solution:**
1. Update yt-dlp: `pip install -U yt-dlp`
2. Check URL is valid
3. Some videos are region-restricted

### AssemblyAI API Error

```
Error: Unauthorized
```

**Solution:**
1. Check API key in `.env`
2. Verify key is valid at assemblyai.com
3. Check account has credits

## 📈 Performance Tips

1. **Use AssemblyAI for speed:**
   - 10x faster than local Whisper
   - Better accuracy
   - Speaker diarization included

2. **Batch process videos:**
   - Process multiple videos overnight
   - Use local Whisper to save API costs

3. **Optimize clip generation:**
   - Adjust scene threshold for your content type
   - Skip clip splitting if not needed

4. **Cache processed videos:**
   - Results saved in `output/videos/transcripts/`
   - Reuse processed data
   - Don't reprocess same video

## 🔐 Privacy & Security

- All processing can be done locally (no cloud required)
- Videos never leave your machine with local Whisper
- AssemblyAI: Videos uploaded for processing, then deleted
- Social media: Only public data is fetched
- No data stored on our servers

## 🚀 Next Steps

1. **Install dependencies**: `pip install -r requirements-video.txt`
2. **Get AssemblyAI key**: https://assemblyai.com (optional)
3. **Test with sample video**: Process a short video to verify setup
4. **Integrate with workflows**: Add video nodes to your canvas workflows
5. **Explore social media**: Try different URL types

## 📚 Additional Resources

- FFmpeg Documentation: https://ffmpeg.org/documentation.html
- Whisper GitHub: https://github.com/openai/whisper
- AssemblyAI Docs: https://assemblyai.com/docs
- yt-dlp GitHub: https://github.com/yt-dlp/yt-dlp

## 💡 Advanced Tips

### Combine with Outreach Workflows

1. Process competitor videos
2. Extract key points
3. Use insights for outreach messaging
4. Reference specific timestamps in emails

### Automate Content Creation

1. Process long-form video
2. Auto-generate clips
3. Use transcripts for blog posts
4. Create social media snippets

### Research & Analysis

1. Process interview videos
2. Extract quotes by speaker
3. Build timeline of topics
4. Generate research summaries

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
