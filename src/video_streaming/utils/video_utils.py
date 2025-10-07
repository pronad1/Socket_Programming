#!/usr/bin/env python3
"""
Video Streaming Utilities
Common utilities for video streaming operations

This module provides:
- Video file validation and information extraction
- Format conversion utilities
- Quality profile management
- Bitrate calculation
- Frame rate detection
- Video metadata parsing

Author: Prosenjit Mondol
Date: October 2025
Project: Professional Video Streaming System
"""

import os
import json
import subprocess
import mimetypes
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import time


class VideoFormat(Enum):
    """Supported video formats"""
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    OGV = "ogv"


class VideoCodec(Enum):
    """Supported video codecs"""
    H264 = "h264"
    H265 = "h265"
    VP8 = "vp8"
    VP9 = "vp9"
    AV1 = "av1"
    MPEG4 = "mpeg4"
    MPEG2 = "mpeg2"


class AudioCodec(Enum):
    """Supported audio codecs"""
    AAC = "aac"
    MP3 = "mp3"
    AC3 = "ac3"
    DTS = "dts"
    FLAC = "flac"
    VORBIS = "vorbis"
    OPUS = "opus"


@dataclass
class VideoQualityProfile:
    """Video quality profile configuration"""
    name: str
    resolution: Tuple[int, int]  # (width, height)
    bitrate: int  # in kbps
    framerate: int  # fps
    codec: VideoCodec = VideoCodec.H264
    audio_bitrate: int = 128  # kbps
    audio_codec: AudioCodec = AudioCodec.AAC
    
    @property
    def resolution_string(self) -> str:
        """Get resolution as string (e.g., '1920x1080')"""
        return f"{self.resolution[0]}x{self.resolution[1]}"
    
    @property
    def is_hd(self) -> bool:
        """Check if profile is HD quality"""
        return self.resolution[1] >= 720
    
    @property
    def is_4k(self) -> bool:
        """Check if profile is 4K quality"""
        return self.resolution[1] >= 2160


@dataclass
class VideoInfo:
    """Video file information"""
    filename: str
    filepath: str
    size: int  # bytes
    duration: float  # seconds
    resolution: Tuple[int, int]
    framerate: float
    bitrate: int  # kbps
    video_codec: str
    audio_codec: str
    format: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes"""
        return self.size / (1024 * 1024)
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)"""
        hours = int(self.duration // 3600)
        minutes = int((self.duration % 3600) // 60)
        seconds = int(self.duration % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def resolution_string(self) -> str:
        """Get resolution as string"""
        return f"{self.resolution[0]}x{self.resolution[1]}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.filename,
            'path': self.filepath,
            'size': self.size,
            'duration': self.duration,
            'resolution': self.resolution_string,
            'framerate': self.framerate,
            'bitrate': self.bitrate,
            'video_codec': self.video_codec,
            'audio_codec': self.audio_codec,
            'format': self.format,
            'description': f"{self.resolution_string} {self.video_codec.upper()} video",
            'metadata': self.metadata
        }


class QualityProfileManager:
    """Manage video quality profiles"""
    
    # Predefined quality profiles
    PROFILES = {
        "480p": VideoQualityProfile(
            name="480p",
            resolution=(854, 480),
            bitrate=1000,
            framerate=30,
            codec=VideoCodec.H264
        ),
        "720p": VideoQualityProfile(
            name="720p", 
            resolution=(1280, 720),
            bitrate=2500,
            framerate=30,
            codec=VideoCodec.H264
        ),
        "1080p": VideoQualityProfile(
            name="1080p",
            resolution=(1920, 1080),
            bitrate=5000,
            framerate=30,
            codec=VideoCodec.H264
        ),
        "4K": VideoQualityProfile(
            name="4K",
            resolution=(3840, 2160),
            bitrate=15000,
            framerate=30,
            codec=VideoCodec.H264
        )
    }
    
    @classmethod
    def get_profile(cls, name: str) -> Optional[VideoQualityProfile]:
        """Get quality profile by name"""
        return cls.PROFILES.get(name)
    
    @classmethod
    def get_all_profiles(cls) -> Dict[str, VideoQualityProfile]:
        """Get all quality profiles"""
        return cls.PROFILES.copy()
    
    @classmethod
    def get_profile_names(cls) -> List[str]:
        """Get list of profile names"""
        return list(cls.PROFILES.keys())
    
    @classmethod
    def get_best_profile_for_resolution(cls, resolution: Tuple[int, int]) -> VideoQualityProfile:
        """Get best quality profile for given resolution"""
        width, height = resolution
        
        # Find the best matching profile
        best_profile = cls.PROFILES["480p"]  # Default
        
        for profile in cls.PROFILES.values():
            profile_width, profile_height = profile.resolution
            if height >= profile_height and width >= profile_width:
                best_profile = profile
        
        return best_profile
    
    @classmethod
    def create_custom_profile(cls, name: str, resolution: Tuple[int, int], 
                            bitrate: int, framerate: int = 30,
                            codec: VideoCodec = VideoCodec.H264) -> VideoQualityProfile:
        """Create custom quality profile"""
        return VideoQualityProfile(
            name=name,
            resolution=resolution,
            bitrate=bitrate,
            framerate=framerate,
            codec=codec
        )


class VideoFileValidator:
    """Validate and analyze video files"""
    
    SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.ogv'}
    SUPPORTED_MIMETYPES = {
        'video/mp4', 'video/avi', 'video/x-msvideo', 'video/quicktime',
        'video/x-ms-wmv', 'video/x-flv', 'video/webm', 'video/ogg'
    }
    
    @classmethod
    def is_valid_video_file(cls, filepath: str) -> bool:
        """Check if file is a valid video file"""
        if not os.path.isfile(filepath):
            return False
        
        # Check file extension
        _, ext = os.path.splitext(filepath.lower())
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return False
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type and mime_type not in cls.SUPPORTED_MIMETYPES:
            return False
        
        # Check if file is readable
        try:
            with open(filepath, 'rb') as f:
                # Read first few bytes to check if it's a valid video file
                header = f.read(32)
                return len(header) > 0
        except (IOError, OSError):
            return False
    
    @classmethod
    def get_video_info(cls, filepath: str, use_ffprobe: bool = True) -> Optional[VideoInfo]:
        """Get detailed video file information"""
        if not cls.is_valid_video_file(filepath):
            return None
        
        try:
            if use_ffprobe and cls._is_ffprobe_available():
                return cls._get_video_info_ffprobe(filepath)
            else:
                return cls._get_video_info_basic(filepath)
        except Exception as e:
            print(f"Error getting video info for {filepath}: {e}")
            return cls._get_video_info_basic(filepath)
    
    @classmethod
    def _is_ffprobe_available(cls) -> bool:
        """Check if ffprobe is available"""
        try:
            subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @classmethod
    def _get_video_info_ffprobe(cls, filepath: str) -> VideoInfo:
        """Get video info using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', filepath
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Extract format information
        format_info = data.get('format', {})
        duration = float(format_info.get('duration', 0))
        size = int(format_info.get('size', 0))
        bitrate = int(format_info.get('bit_rate', 0)) // 1000  # Convert to kbps
        
        # Find video and audio streams
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video' and video_stream is None:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and audio_stream is None:
                audio_stream = stream
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        # Extract video information
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        framerate_str = video_stream.get('r_frame_rate', '30/1')
        
        # Parse framerate
        if '/' in framerate_str:
            num, den = framerate_str.split('/')
            framerate = float(num) / float(den) if float(den) != 0 else 30.0
        else:
            framerate = float(framerate_str)
        
        video_codec = video_stream.get('codec_name', 'unknown')
        audio_codec = audio_stream.get('codec_name', 'unknown') if audio_stream else 'none'
        
        # Get format
        format_name = format_info.get('format_name', '').split(',')[0]
        
        # Create metadata
        metadata = {
            'ffprobe_data': data,
            'video_stream': video_stream,
            'audio_stream': audio_stream
        }
        
        filename = os.path.basename(filepath)
        
        return VideoInfo(
            filename=filename,
            filepath=filepath,
            size=size,
            duration=duration,
            resolution=(width, height),
            framerate=framerate,
            bitrate=bitrate,
            video_codec=video_codec,
            audio_codec=audio_codec,
            format=format_name,
            metadata=metadata
        )
    
    @classmethod
    def _get_video_info_basic(cls, filepath: str) -> VideoInfo:
        """Get basic video info without ffprobe"""
        stat = os.stat(filepath)
        size = stat.st_size
        filename = os.path.basename(filepath)
        
        # Guess format from extension
        _, ext = os.path.splitext(filepath.lower())
        format_name = ext[1:] if ext else 'unknown'
        
        # Default values (would need proper video analysis for accurate info)
        return VideoInfo(
            filename=filename,
            filepath=filepath,
            size=size,
            duration=60.0,  # Default duration
            resolution=(1280, 720),  # Default resolution
            framerate=30.0,  # Default framerate
            bitrate=2500,  # Default bitrate
            video_codec='h264',  # Default codec
            audio_codec='aac',  # Default audio codec
            format=format_name,
            metadata={'method': 'basic', 'note': 'Estimated values'}
        )


class VideoLibraryManager:
    """Manage video library and metadata"""
    
    def __init__(self, library_path: str):
        """
        Initialize video library manager
        
        Args:
            library_path: Path to video library directory
        """
        self.library_path = library_path
        self.videos: Dict[str, VideoInfo] = {}
        self.metadata_file = os.path.join(library_path, '.video_metadata.json')
        
        # Ensure library directory exists
        os.makedirs(library_path, exist_ok=True)
        
        # Load existing metadata
        self.load_metadata()
    
    def scan_library(self, force_rescan: bool = False) -> int:
        """
        Scan library directory for video files
        
        Args:
            force_rescan: Force rescan even if metadata exists
            
        Returns:
            Number of videos found
        """
        videos_found = 0
        
        for root, dirs, files in os.walk(self.library_path):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Skip metadata file
                if file == '.video_metadata.json':
                    continue
                
                # Check if it's a video file
                if VideoFileValidator.is_valid_video_file(filepath):
                    filename = os.path.basename(filepath)
                    
                    # Skip if already scanned and not forcing rescan
                    if filename in self.videos and not force_rescan:
                        videos_found += 1
                        continue
                    
                    # Get video information
                    video_info = VideoFileValidator.get_video_info(filepath)
                    if video_info:
                        self.videos[filename] = video_info
                        videos_found += 1
        
        # Save updated metadata
        self.save_metadata()
        
        return videos_found
    
    def get_video_list(self) -> List[Dict]:
        """Get list of all videos in library"""
        return [video.to_dict() for video in self.videos.values()]
    
    def get_video_info(self, filename: str) -> Optional[VideoInfo]:
        """Get video information by filename"""
        return self.videos.get(filename)
    
    def add_video(self, filepath: str) -> bool:
        """Add single video to library"""
        if not VideoFileValidator.is_valid_video_file(filepath):
            return False
        
        video_info = VideoFileValidator.get_video_info(filepath)
        if video_info:
            self.videos[video_info.filename] = video_info
            self.save_metadata()
            return True
        
        return False
    
    def remove_video(self, filename: str) -> bool:
        """Remove video from library"""
        if filename in self.videos:
            del self.videos[filename]
            self.save_metadata()
            return True
        return False
    
    def search_videos(self, query: str) -> List[Dict]:
        """Search videos by name or metadata"""
        query = query.lower()
        results = []
        
        for video in self.videos.values():
            if (query in video.filename.lower() or 
                query in video.video_codec.lower() or
                query in video.format.lower()):
                results.append(video.to_dict())
        
        return results
    
    def get_videos_by_quality(self, quality: str) -> List[Dict]:
        """Get videos by quality profile"""
        profile = QualityProfileManager.get_profile(quality)
        if not profile:
            return []
        
        results = []
        for video in self.videos.values():
            # Check if video resolution matches or exceeds profile
            if (video.resolution[1] >= profile.resolution[1] and
                video.resolution[0] >= profile.resolution[0]):
                results.append(video.to_dict())
        
        return results
    
    def load_metadata(self):
        """Load video metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Convert back to VideoInfo objects
                for filename, video_data in data.items():
                    if isinstance(video_data, dict):
                        # Reconstruct VideoInfo from saved data
                        resolution = video_data.get('resolution', '1280x720')
                        if 'x' in resolution:
                            width, height = map(int, resolution.split('x'))
                        else:
                            width, height = 1280, 720
                        
                        video_info = VideoInfo(
                            filename=video_data.get('name', filename),
                            filepath=video_data.get('path', ''),
                            size=video_data.get('size', 0),
                            duration=video_data.get('duration', 0),
                            resolution=(width, height),
                            framerate=video_data.get('framerate', 30),
                            bitrate=video_data.get('bitrate', 2500),
                            video_codec=video_data.get('video_codec', 'h264'),
                            audio_codec=video_data.get('audio_codec', 'aac'),
                            format=video_data.get('format', 'mp4'),
                            metadata=video_data.get('metadata', {})
                        )
                        
                        self.videos[filename] = video_info
            
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading metadata: {e}")
    
    def save_metadata(self):
        """Save video metadata to file"""
        try:
            data = {}
            for filename, video in self.videos.items():
                data[filename] = video.to_dict()
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except IOError as e:
            print(f"Error saving metadata: {e}")
    
    def get_library_stats(self) -> Dict:
        """Get library statistics"""
        total_videos = len(self.videos)
        total_size = sum(video.size for video in self.videos.values())
        total_duration = sum(video.duration for video in self.videos.values())
        
        # Count by format
        format_counts = {}
        for video in self.videos.values():
            format_counts[video.format] = format_counts.get(video.format, 0) + 1
        
        # Count by resolution
        resolution_counts = {}
        for video in self.videos.values():
            res_str = video.resolution_string
            resolution_counts[res_str] = resolution_counts.get(res_str, 0) + 1
        
        return {
            'total_videos': total_videos,
            'total_size': total_size,
            'total_size_gb': total_size / (1024 ** 3),
            'total_duration': total_duration,
            'total_duration_hours': total_duration / 3600,
            'format_distribution': format_counts,
            'resolution_distribution': resolution_counts,
            'average_bitrate': sum(video.bitrate for video in self.videos.values()) / total_videos if total_videos > 0 else 0
        }


class StreamingUtils:
    """Streaming-related utility functions"""
    
    @staticmethod
    def calculate_chunk_size(bitrate: int, fps: int = 30) -> int:
        """Calculate optimal chunk size for streaming"""
        # Calculate bytes per frame
        bytes_per_second = (bitrate * 1000) // 8  # Convert kbps to bytes
        bytes_per_frame = bytes_per_second // fps
        
        # Ensure minimum chunk size
        return max(1024, bytes_per_frame)
    
    @staticmethod
    def estimate_buffer_size(bitrate: int, buffer_seconds: float = 5.0) -> int:
        """Estimate buffer size needed for smooth playback"""
        bytes_per_second = (bitrate * 1000) // 8
        return int(bytes_per_second * buffer_seconds)
    
    @staticmethod
    def validate_streaming_parameters(bitrate: int, resolution: Tuple[int, int], 
                                    fps: int) -> List[str]:
        """Validate streaming parameters and return warnings"""
        warnings = []
        
        width, height = resolution
        
        # Check bitrate vs resolution
        if height >= 1080 and bitrate < 3000:
            warnings.append("Bitrate too low for 1080p resolution (recommended: 3000+ kbps)")
        elif height >= 720 and bitrate < 1500:
            warnings.append("Bitrate too low for 720p resolution (recommended: 1500+ kbps)")
        
        # Check frame rate
        if fps > 60:
            warnings.append("High frame rate may cause compatibility issues")
        elif fps < 15:
            warnings.append("Low frame rate may result in choppy playback")
        
        # Check aspect ratio
        aspect_ratio = width / height
        common_ratios = [16/9, 4/3, 21/9, 1/1]
        if not any(abs(aspect_ratio - ratio) < 0.1 for ratio in common_ratios):
            warnings.append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
        
        return warnings
    
    @staticmethod
    def generate_file_hash(filepath: str, algorithm: str = 'md5') -> str:
        """Generate hash for file integrity checking"""
        hash_algo = hashlib.new(algorithm)
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_algo.update(chunk)
            return hash_algo.hexdigest()
        except IOError:
            return ""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def format_bitrate(bitrate_bps: int) -> str:
        """Format bitrate in human readable format"""
        if bitrate_bps < 1000:
            return f"{bitrate_bps} bps"
        elif bitrate_bps < 1000000:
            return f"{bitrate_bps / 1000:.1f} kbps"
        else:
            return f"{bitrate_bps / 1000000:.1f} Mbps"


if __name__ == "__main__":
    # Example usage
    print("🎬 Video Streaming Utilities")
    print("   📹 Video file validation and analysis")
    
    # Test quality profiles
    profile = QualityProfileManager.get_profile("1080p")
    if profile:
        print(f"   ✅ 1080p profile: {profile.resolution_string} @ {profile.bitrate} kbps")
    
    # Test video validator
    test_files = ["test.mp4", "nonexistent.avi"]
    for test_file in test_files:
        is_valid = VideoFileValidator.is_valid_video_file(test_file)
        print(f"   📄 {test_file}: {'Valid' if is_valid else 'Invalid'}")
    
    # Test streaming utils
    chunk_size = StreamingUtils.calculate_chunk_size(2500, 30)
    buffer_size = StreamingUtils.estimate_buffer_size(2500, 5.0)
    print(f"   📊 Streaming: chunk={chunk_size} bytes, buffer={buffer_size} bytes")
    
    file_size = StreamingUtils.format_file_size(1073741824)
    bitrate = StreamingUtils.format_bitrate(2500000)
    print(f"   📏 Formats: {file_size}, {bitrate}")