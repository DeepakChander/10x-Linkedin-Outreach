#!/usr/bin/env python3
"""
Video Processor - Advanced video analysis, transcription, and clip generation

Features:
- Video upload and processing
- AI transcription with timestamps
- Speaker diarization (who spoke when)
- Video clip splitting
- Scene detection
- Summary generation with timestamps
- YouTube video processing
- Social media link processing (LinkedIn, Instagram, Reddit)

Dependencies:
    pip install openai-whisper pillow moviepy yt-dlp beautifulsoup4 requests
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta
import urllib.request
import urllib.parse

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
VIDEO_OUTPUT_DIR = OUTPUT_DIR / "videos"
CLIPS_DIR = VIDEO_OUTPUT_DIR / "clips"
TRANSCRIPTS_DIR = VIDEO_OUTPUT_DIR / "transcripts"
THUMBNAILS_DIR = VIDEO_OUTPUT_DIR / "thumbnails"

# Ensure directories exist
for dir_path in [VIDEO_OUTPUT_DIR, CLIPS_DIR, TRANSCRIPTS_DIR, THUMBNAILS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class VideoProcessor:
    """Process videos with AI-powered transcription and analysis"""

    def __init__(self, use_cloud_api: bool = True):
        """
        Initialize video processor

        Args:
            use_cloud_api: Use cloud APIs (AssemblyAI, OpenAI) vs local Whisper
        """
        self.use_cloud_api = use_cloud_api

    def process_video(
        self,
        video_path: str,
        output_name: Optional[str] = None,
        split_by_scene: bool = True,
        transcribe: bool = True,
        generate_summary: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a video file completely

        Args:
            video_path: Path to video file or data URL
            output_name: Custom output name
            split_by_scene: Split video into clips by scene
            transcribe: Generate transcription
            generate_summary: Generate AI summary

        Returns:
            Processing results with clips, transcripts, and summaries
        """
        print(f"🎥 Processing video: {video_path}")

        # Handle data URL
        if video_path.startswith('data:'):
            video_path = self._save_data_url_video(video_path, output_name)

        video_path = Path(video_path)
        if not video_path.exists():
            return {"error": f"Video file not found: {video_path}"}

        results = {
            "video_path": str(video_path),
            "duration": self._get_video_duration(video_path),
            "clips": [],
            "transcript": None,
            "summary": None,
            "thumbnail": None,
        }

        # Generate thumbnail
        print("📸 Generating thumbnail...")
        results["thumbnail"] = self._generate_thumbnail(video_path)

        # Transcribe video
        if transcribe:
            print("🎙️ Transcribing audio...")
            results["transcript"] = self._transcribe_video(video_path)

        # Split into clips
        if split_by_scene:
            print("✂️ Splitting video into clips...")
            results["clips"] = self._split_by_scenes(video_path)

        # Generate summary
        if generate_summary and results.get("transcript"):
            print("📝 Generating AI summary...")
            results["summary"] = self._generate_summary(results["transcript"])

        # Save results
        output_file = TRANSCRIPTS_DIR / f"{video_path.stem}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"✅ Processing complete! Results saved to {output_file}")
        return results

    def _save_data_url_video(self, data_url: str, output_name: Optional[str] = None) -> Path:
        """Save data URL video to file"""
        import base64

        # Extract video data
        if ',' in data_url:
            header, data = data_url.split(',', 1)
            video_data = base64.b64decode(data)

            # Determine extension
            ext = 'mp4'
            if 'video/webm' in header:
                ext = 'webm'
            elif 'video/mov' in header:
                ext = 'mov'

            # Save file
            name = output_name or f"video_{os.urandom(4).hex()}"
            output_path = VIDEO_OUTPUT_DIR / f"{name}.{ext}"

            with open(output_path, 'wb') as f:
                f.write(video_data)

            return output_path

        return Path(data_url)

    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"Warning: Could not get duration: {e}")
            return 0.0

    def _generate_thumbnail(self, video_path: Path) -> str:
        """Generate thumbnail from video at 1 second"""
        try:
            thumbnail_path = THUMBNAILS_DIR / f"{video_path.stem}_thumb.jpg"
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', '00:00:01',
                '-vframes', '1',
                '-y',
                str(thumbnail_path)
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
            return str(thumbnail_path)
        except Exception as e:
            print(f"Warning: Could not generate thumbnail: {e}")
            return ""

    def _transcribe_video(self, video_path: Path) -> Dict[str, Any]:
        """
        Transcribe video using Whisper (local or API)

        Returns transcript with timestamps and speaker diarization
        """
        # Extract audio first
        audio_path = VIDEO_OUTPUT_DIR / f"{video_path.stem}_audio.wav"

        try:
            # Extract audio using ffmpeg
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',
                '-ar', '16000',  # 16kHz for Whisper
                '-ac', '1',  # Mono
                '-y',
                str(audio_path)
            ]
            subprocess.run(cmd, capture_output=True, timeout=300)

            if self.use_cloud_api:
                return self._transcribe_with_assemblyai(audio_path)
            else:
                return self._transcribe_with_local_whisper(audio_path)

        except Exception as e:
            print(f"Error transcribing: {e}")
            return {
                "error": str(e),
                "text": "",
                "segments": [],
                "speakers": []
            }
        finally:
            # Clean up audio file
            if audio_path.exists():
                audio_path.unlink()

    def _transcribe_with_local_whisper(self, audio_path: Path) -> Dict[str, Any]:
        """Use local Whisper for transcription"""
        try:
            import whisper

            # Load model (base is fast, large is accurate)
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(
                str(audio_path),
                word_timestamps=True,
                verbose=False
            )

            # Format results
            segments = []
            for segment in result['segments']:
                segments.append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "text": segment['text'].strip(),
                    "speaker": "Unknown",  # Whisper doesn't do diarization
                })

            return {
                "text": result['text'],
                "segments": segments,
                "speakers": ["Unknown"],
                "language": result.get('language', 'en'),
            }

        except ImportError:
            return {
                "error": "Whisper not installed. Run: pip install openai-whisper",
                "text": "",
                "segments": [],
                "speakers": []
            }
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "segments": [],
                "speakers": []
            }

    def _transcribe_with_assemblyai(self, audio_path: Path) -> Dict[str, Any]:
        """Use AssemblyAI API for transcription with speaker diarization"""
        # Check for API key
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            print("⚠️ ASSEMBLYAI_API_KEY not set. Using local Whisper instead.")
            return self._transcribe_with_local_whisper(audio_path)

        try:
            import requests

            # Upload audio
            print("  Uploading audio to AssemblyAI...")
            headers = {'authorization': api_key}

            with open(audio_path, 'rb') as f:
                response = requests.post(
                    'https://api.assemblyai.com/v2/upload',
                    headers=headers,
                    files={'file': f}
                )
            upload_url = response.json()['upload_url']

            # Request transcription with speaker diarization
            print("  Requesting transcription...")
            transcript_request = {
                'audio_url': upload_url,
                'speaker_labels': True,  # Enable speaker diarization
                'auto_highlights': True,
            }

            response = requests.post(
                'https://api.assemblyai.com/v2/transcript',
                json=transcript_request,
                headers=headers
            )
            transcript_id = response.json()['id']

            # Poll for completion
            print("  Waiting for transcription...")
            while True:
                response = requests.get(
                    f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                    headers=headers
                )
                data = response.json()

                if data['status'] == 'completed':
                    break
                elif data['status'] == 'error':
                    return {"error": data.get('error', 'Transcription failed')}

                import time
                time.sleep(3)

            # Format results
            segments = []
            speakers = set()

            for utterance in data.get('utterances', []):
                speaker = f"Speaker {utterance['speaker']}"
                speakers.add(speaker)
                segments.append({
                    "start": utterance['start'] / 1000,  # Convert ms to seconds
                    "end": utterance['end'] / 1000,
                    "text": utterance['text'],
                    "speaker": speaker,
                })

            return {
                "text": data['text'],
                "segments": segments,
                "speakers": sorted(list(speakers)),
                "confidence": data.get('confidence', 0),
            }

        except Exception as e:
            print(f"AssemblyAI error: {e}. Falling back to local Whisper.")
            return self._transcribe_with_local_whisper(audio_path)

    def _split_by_scenes(self, video_path: Path) -> List[Dict[str, Any]]:
        """Split video into clips based on scene detection"""
        try:
            # Use ffmpeg scene detection
            scenes = self._detect_scenes(video_path)

            clips = []
            for i, (start, end) in enumerate(scenes):
                clip_name = f"{video_path.stem}_clip_{i+1:03d}.mp4"
                clip_path = CLIPS_DIR / clip_name

                # Extract clip
                duration = end - start
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-ss', str(start),
                    '-t', str(duration),
                    '-c', 'copy',
                    '-y',
                    str(clip_path)
                ]
                subprocess.run(cmd, capture_output=True, timeout=60)

                clips.append({
                    "clip_number": i + 1,
                    "start_time": start,
                    "end_time": end,
                    "duration": duration,
                    "path": str(clip_path),
                })

            return clips

        except Exception as e:
            print(f"Error splitting video: {e}")
            return []

    def _detect_scenes(self, video_path: Path, threshold: float = 0.3) -> List[Tuple[float, float]]:
        """Detect scene changes using ffmpeg"""
        try:
            # Use ffmpeg select filter to detect scene changes
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-filter:v', f'select=gt(scene\\,{threshold}),showinfo',
                '-f', 'null',
                '-'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Parse scene timestamps from stderr
            scene_times = [0.0]
            for line in result.stderr.split('\n'):
                if 'pts_time:' in line:
                    try:
                        time_str = line.split('pts_time:')[1].split()[0]
                        scene_times.append(float(time_str))
                    except:
                        pass

            # Add end time
            duration = self._get_video_duration(video_path)
            scene_times.append(duration)

            # Create scene pairs
            scenes = []
            for i in range(len(scene_times) - 1):
                scenes.append((scene_times[i], scene_times[i + 1]))

            return scenes if len(scenes) > 1 else [(0, duration)]

        except Exception as e:
            # Fallback: split into 30-second chunks
            duration = self._get_video_duration(video_path)
            chunk_duration = 30
            scenes = []

            current = 0
            while current < duration:
                end = min(current + chunk_duration, duration)
                scenes.append((current, end))
                current = end

            return scenes

    def _generate_summary(self, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI summary from transcript with timestamps"""
        segments = transcript.get('segments', [])
        if not segments:
            return {"error": "No transcript segments to summarize"}

        # Build formatted transcript with timestamps
        formatted_transcript = []
        for seg in segments:
            time_str = self._format_timestamp(seg['start'])
            speaker = seg.get('speaker', 'Unknown')
            text = seg['text']
            formatted_transcript.append(f"[{time_str}] {speaker}: {text}")

        full_text = '\n'.join(formatted_transcript)

        # Generate summary structure
        summary = {
            "full_transcript": full_text,
            "key_points": self._extract_key_points(segments),
            "timeline": self._build_timeline(segments),
            "speakers_summary": self._summarize_speakers(segments),
            "action_items": self._extract_action_items(full_text),
        }

        return summary

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to HH:MM:SS"""
        td = timedelta(seconds=int(seconds))
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def _extract_key_points(self, segments: List[Dict]) -> List[str]:
        """Extract key points from segments (simplified)"""
        # Group segments into chunks
        chunk_size = 5
        key_points = []

        for i in range(0, len(segments), chunk_size):
            chunk = segments[i:i+chunk_size]
            if chunk:
                text = ' '.join([s['text'] for s in chunk])
                # Simple heuristic: longer sentences are more important
                if len(text.split()) > 15:
                    key_points.append({
                        "timestamp": self._format_timestamp(chunk[0]['start']),
                        "point": text[:200] + '...' if len(text) > 200 else text
                    })

        return key_points[:10]  # Top 10 key points

    def _build_timeline(self, segments: List[Dict]) -> List[Dict]:
        """Build timeline of major topics"""
        timeline = []
        current_topic = None
        current_start = 0

        for i, seg in enumerate(segments):
            # Simple topic detection: look for topic changes
            if i == 0 or i % 10 == 0 or i == len(segments) - 1:
                if current_topic:
                    timeline.append({
                        "start": self._format_timestamp(current_start),
                        "end": self._format_timestamp(seg['start']),
                        "topic": current_topic[:100]
                    })

                current_topic = seg['text']
                current_start = seg['start']

        return timeline

    def _summarize_speakers(self, segments: List[Dict]) -> Dict[str, Any]:
        """Summarize who spoke when and how much"""
        speakers = {}

        for seg in segments:
            speaker = seg.get('speaker', 'Unknown')
            if speaker not in speakers:
                speakers[speaker] = {
                    "total_time": 0,
                    "segments": 0,
                    "first_appearance": self._format_timestamp(seg['start'])
                }

            speakers[speaker]['total_time'] += seg['end'] - seg['start']
            speakers[speaker]['segments'] += 1

        # Format total time
        for speaker_data in speakers.values():
            speaker_data['total_time_formatted'] = self._format_timestamp(speaker_data['total_time'])

        return speakers

    def _extract_action_items(self, text: str) -> List[str]:
        """Extract potential action items from text"""
        action_words = ['should', 'need to', 'must', 'will', 'going to', 'todo', 'action']
        action_items = []

        for line in text.split('\n'):
            if any(word in line.lower() for word in action_words):
                # Extract the sentence
                parts = line.split(']', 1)
                if len(parts) > 1:
                    action_items.append(parts[1].strip())

        return action_items[:5]  # Top 5 action items


class URLProcessor:
    """Process URLs from YouTube, LinkedIn, Instagram, Reddit"""

    def process_url(self, url: str) -> Dict[str, Any]:
        """Process any supported URL"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return self.process_youtube(url)
        elif 'linkedin.com' in url:
            return self.process_linkedin(url)
        elif 'instagram.com' in url:
            return self.process_instagram(url)
        elif 'reddit.com' in url:
            return self.process_reddit(url)
        else:
            return {"error": "Unsupported URL"}

    def process_youtube(self, url: str) -> Dict[str, Any]:
        """Download and process YouTube video"""
        try:
            print(f"📺 Processing YouTube: {url}")

            # Download video using yt-dlp
            output_template = str(VIDEO_OUTPUT_DIR / 'youtube_%(id)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '-f', 'best[ext=mp4]',
                '-o', output_template,
                '--print', 'after_move:filepath',
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            video_path = result.stdout.strip()

            if not video_path or not os.path.exists(video_path):
                return {"error": "Failed to download YouTube video"}

            # Process the downloaded video
            processor = VideoProcessor()
            return processor.process_video(video_path)

        except Exception as e:
            return {"error": f"YouTube processing failed: {e}"}

    def process_linkedin(self, url: str) -> Dict[str, Any]:
        """Fetch LinkedIn post content"""
        try:
            print(f"💼 Processing LinkedIn: {url}")

            # Use requests to fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')

            # Extract basic info (simplified - would need proper parsing)
            from html.parser import HTMLParser

            class LinkedInParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.images = []

                def handle_data(self, data):
                    if data.strip():
                        self.text.append(data.strip())

            parser = LinkedInParser()
            parser.feed(html)

            return {
                "platform": "linkedin",
                "url": url,
                "text": ' '.join(parser.text[:50]),  # First 50 text chunks
                "images": [],  # Would need more sophisticated extraction
                "fetched_at": str(datetime.now())
            }

        except Exception as e:
            return {"error": f"LinkedIn processing failed: {e}"}

    def process_instagram(self, url: str) -> Dict[str, Any]:
        """Fetch Instagram post content"""
        print(f"📸 Processing Instagram: {url}")
        # Instagram requires authentication - would need Instagram API or browser automation
        return {
            "platform": "instagram",
            "url": url,
            "note": "Instagram processing requires authentication. Use Browser-Use MCP for full access.",
            "suggestion": "Use the instagram-adapter.py with Browser-Use MCP to fetch post data"
        }

    def process_reddit(self, url: str) -> Dict[str, Any]:
        """Fetch Reddit post content"""
        try:
            print(f"🔴 Processing Reddit: {url}")

            # Add .json to get JSON response
            json_url = url.rstrip('/') + '.json'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }

            req = urllib.request.Request(json_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            # Extract post data
            post = data[0]['data']['children'][0]['data']

            return {
                "platform": "reddit",
                "url": url,
                "title": post.get('title', ''),
                "text": post.get('selftext', ''),
                "author": post.get('author', ''),
                "score": post.get('score', 0),
                "num_comments": post.get('num_comments', 0),
                "created": post.get('created_utc', 0),
                "subreddit": post.get('subreddit', ''),
            }

        except Exception as e:
            return {"error": f"Reddit processing failed: {e}"}


def main():
    """CLI interface for video processing"""
    if len(sys.argv) < 2:
        print("""
Video Processor - Advanced Video Analysis

Usage:
  python video_processor.py <command> [args]

Commands:
  process <video_file>        Process a local video file
  youtube <url>               Process a YouTube video
  url <url>                   Process any supported URL (YouTube, LinkedIn, Reddit)

Examples:
  python video_processor.py process video.mp4
  python video_processor.py youtube https://youtube.com/watch?v=...
  python video_processor.py url https://linkedin.com/posts/...
        """)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'process' and len(sys.argv) > 2:
        processor = VideoProcessor()
        result = processor.process_video(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == 'youtube' and len(sys.argv) > 2:
        url_processor = URLProcessor()
        result = url_processor.process_youtube(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == 'url' and len(sys.argv) > 2:
        url_processor = URLProcessor()
        result = url_processor.process_url(sys.argv[2])
        print(json.dumps(result, indent=2))

    else:
        print("Invalid command or missing arguments")
        sys.exit(1)


if __name__ == '__main__':
    from datetime import datetime
    main()
