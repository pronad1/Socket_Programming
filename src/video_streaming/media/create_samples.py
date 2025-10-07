# Sample Media Files for Video Streaming
# These are placeholder files for testing the video streaming system

# Create sample video files with dummy content
import os

def create_sample_video(filename, size_mb=10):
    """Create a sample video file with dummy data"""
    # MP4 file header (simplified)
    mp4_header = b'\\x00\\x00\\x00\\x20ftypmp42\\x00\\x00\\x00\\x00mp42isom'
    
    # Calculate size in bytes
    size_bytes = size_mb * 1024 * 1024
    
    with open(filename, 'wb') as f:
        f.write(mp4_header)
        
        # Fill with dummy data
        chunk_size = 4096
        written = len(mp4_header)
        
        while written < size_bytes:
            remaining = size_bytes - written
            chunk_data = b'\\x00' * min(chunk_size, remaining)
            f.write(chunk_data)
            written += len(chunk_data)

# Create sample videos
if __name__ == "__main__":
    # Create media directory if it doesn't exist
    media_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Sample videos with different qualities
    videos = [
        ("sample_480p.mp4", 5),   # 5MB sample for 480p
        ("sample_720p.mp4", 15),  # 15MB sample for 720p  
        ("sample_1080p.mp4", 25), # 25MB sample for 1080p
        ("sample_4k.mp4", 50),    # 50MB sample for 4K
        ("demo_video.mp4", 10),   # 10MB demo video
        ("test_stream.mp4", 8),   # 8MB test stream
    ]
    
    for filename, size_mb in videos:
        filepath = os.path.join(media_dir, filename)
        print(f"Creating {filename} ({size_mb}MB)...")
        create_sample_video(filepath, size_mb)
        print(f"✅ Created: {filepath}")
    
    print(f"\\n🎬 Sample media files created in: {media_dir}")
    print("   These files can be used for testing the video streaming system.")
    print("   Replace with real video files for actual streaming.")