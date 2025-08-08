#!/usr/bin/env python3
"""
Enhanced Spotify Playlist to YouTube Downloader - Termux Optimized
Optimized for maximum audio quality and mobile device compatibility.

Features:
- FLAC/320kbps MP3 downloads with highest quality available
- Termux-specific storage handling
- Memory optimization for mobile devices
- Battery and network awareness
- Resume capability for interrupted downloads
- Android notification support
- Progress indicators and mobile-friendly interface
"""

import os
import re
import sys
import time
import json
import signal
import requests
import threading
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import subprocess
import psutil

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from dotenv import load_dotenv

# Import utility modules
from utils.termux_helpers import TermuxHelper
from utils.audio_quality import AudioQualityManager
from utils.mobile_optimizations import MobileOptimizer

# Load environment variables
load_dotenv()

class TermuxSpotifyDownloader:
    def __init__(self):
        print("🎵 Initializing Termux Spotify YouTube Downloader...")
        
        # Initialize helpers
        self.termux_helper = TermuxHelper()
        self.audio_manager = AudioQualityManager()
        self.mobile_optimizer = MobileOptimizer()
        
        # Check Termux environment
        self.is_termux = self.termux_helper.is_termux_environment()
        if self.is_termux:
            print("📱 Termux environment detected - applying mobile optimizations")
        
        # Setup components
        self.setup_spotify()
        self.setup_paths()
        self.setup_youtube_downloader()
        
        # Mobile-specific setup
        self.setup_mobile_features()
        
        # Download state management
        self.download_queue = []
        self.failed_downloads = []
        self.completed_downloads = []
        self.is_downloading = False
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_spotify(self):
        """Initialize Spotify client with error handling"""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Error: Spotify credentials not found!")
            print("Please create a .env file with:")
            print("SPOTIFY_CLIENT_ID=your_client_id")
            print("SPOTIFY_CLIENT_SECRET=your_client_secret")
            print("\nGet credentials from: https://developer.spotify.com/dashboard/")
            sys.exit(1)
            
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test connection with a simple call
            self.spotify.search('test', limit=1, type='artist')
            print("✅ Spotify client initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Spotify client: {e}")
            sys.exit(1)
    
    def setup_paths(self):
        """Setup download paths optimized for Termux/Android"""
        self.script_root = Path(__file__).parent.absolute()
        
        if self.is_termux:
            # Termux-specific paths
            storage_root = Path("/storage/emulated/0")
            if storage_root.exists():
                self.download_root = storage_root / "Music" / "SpotifyDownloads"
                self.temp_dir = storage_root / "Download" / "temp_spotify"
            else:
                # Fallback to Termux home
                home = Path.home()
                self.download_root = home / "storage" / "music" / "SpotifyDownloads"
                self.temp_dir = home / "downloads" / "temp_spotify"
        else:
            # Standard paths for other systems
            self.download_root = self.script_root / "downloads"
            self.temp_dir = self.script_root / "temp"
        
        # Create directories
        self.download_root.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Download path: {self.download_root}")
        print(f"🗂️  Temp path: {self.temp_dir}")
        
        # Check available space
        self.check_storage_space()
    
    def check_storage_space(self):
        """Check available storage space"""
        try:
            if self.is_termux:
                # Use Android storage stats
                result = subprocess.run(['df', '-h', str(self.download_root.parent)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        available = parts[3] if len(parts) > 3 else "Unknown"
                        print(f"💾 Available storage: {available}")
            else:
                # Use psutil for other systems
                usage = psutil.disk_usage(str(self.download_root))
                available_gb = usage.free / (1024**3)
                print(f"💾 Available storage: {available_gb:.1f} GB")
                
        except Exception as e:
            print(f"⚠️  Could not check storage space: {e}")
    
    def setup_youtube_downloader(self):
        """Configure yt-dlp for maximum audio quality"""
        self.ydl_opts = self.audio_manager.get_optimal_ytdl_config(
            temp_dir=str(self.temp_dir),
            is_mobile=self.is_termux
        )
        
        # Add mobile-specific optimizations
        if self.is_termux:
            self.ydl_opts.update(self.mobile_optimizer.get_mobile_ytdl_opts())
        
        print("🎧 YouTube downloader configured for maximum quality")
    
    def setup_mobile_features(self):
        """Setup mobile-specific features"""
        if self.is_termux:
            # Request storage permissions
            self.termux_helper.request_storage_permission()
            
            # Setup notifications
            self.termux_helper.setup_notifications()
            
            # Check battery optimization
            self.mobile_optimizer.check_battery_optimization()
            
            print("📱 Mobile features initialized")
    
    def extract_playlist_id(self, playlist_url):
        """Extract playlist ID from various Spotify URL formats"""
        # Handle different URL formats
        if 'open.spotify.com' in playlist_url:
            if '/playlist/' in playlist_url:
                return playlist_url.split('/playlist/')[-1].split('?')[0]
        
        if playlist_url.startswith('spotify:playlist:'):
            return playlist_url.split('spotify:playlist:')[-1]
        
        # Direct playlist ID
        if len(playlist_url) == 22 and playlist_url.replace('-', '').replace('_', '').isalnum():
            return playlist_url
            
        raise ValueError("Invalid Spotify playlist URL format")
    
    def get_playlist_tracks(self, playlist_url):
        """Get all tracks from Spotify playlist with comprehensive metadata"""
        try:
            playlist_id = self.extract_playlist_id(playlist_url)
            print(f"📋 Fetching playlist: {playlist_id}")
            
            # Get playlist info
            playlist = self.spotify.playlist(playlist_id)
            playlist_name = playlist['name']
            playlist_description = playlist.get('description', '')
            
            print(f"📋 Playlist: {playlist_name}")
            print(f"👤 Owner: {playlist['owner']['display_name']}")
            
            # Get all tracks with pagination
            tracks = []
            results = self.spotify.playlist_tracks(playlist_id, limit=50)
            tracks.extend(results['items'])
            
            while results['next']:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
            
            # Process tracks with detailed metadata
            track_list = []
            for i, item in enumerate(tracks, 1):
                if item['track'] and item['track']['type'] == 'track':
                    track = item['track']
                    
                    # Get album artwork URL (highest resolution)
                    album_cover_url = None
                    if track['album'].get('images'):
                        album_cover_url = max(track['album']['images'], 
                                            key=lambda x: x.get('width', 0))['url']
                    
                    # Parse release date
                    release_date = track['album'].get('release_date', '')
                    release_year = None
                    try:
                        if release_date:
                            release_year = int(release_date.split('-')[0])
                    except:
                        pass
                    
                    track_info = {
                        'index': i,
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'album_artist': track['album']['artists'][0]['name'] if track['album']['artists'] else track['artists'][0]['name'],
                        'track_number': track['track_number'],
                        'disc_number': track.get('disc_number', 1),
                        'duration_ms': track['duration_ms'],
                        'release_year': release_year,
                        'release_date': release_date,
                        'isrc': track['external_ids'].get('isrc', ''),
                        'album_cover_url': album_cover_url,
                        'popularity': track.get('popularity', 0),
                        'explicit': track.get('explicit', False),
                        'preview_url': track.get('preview_url'),
                        'search_query': f"{', '.join([artist['name'] for artist in track['artists']])} - {track['name']}",
                        'spotify_url': track['external_urls']['spotify']
                    }
                    
                    # Get additional artist metadata
                    try:
                        artist_info = self.spotify.artist(track['artists'][0]['id'])
                        track_info['genres'] = artist_info.get('genres', [])[:3]
                    except:
                        track_info['genres'] = []
                    
                    track_list.append(track_info)
                    
                    if i % 10 == 0:
                        print(f"📝 Processed {i}/{len(tracks)} tracks...")
            
            print(f"✅ Found {len(track_list)} tracks")
            
            playlist_info = {
                'name': playlist_name,
                'description': playlist_description,
                'owner': playlist['owner']['display_name'],
                'total_tracks': len(track_list),
                'playlist_id': playlist_id
            }
            
            return playlist_info, track_list
            
        except Exception as e:
            print(f"❌ Error fetching playlist: {e}")
            return None, []
    
    def sanitize_filename(self, filename):
        """Create safe filename for mobile storage"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        # Limit length for mobile compatibility
        max_length = 150 if self.is_termux else 200
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename
    
    def download_album_artwork(self, url, file_path):
        """Download and optimize album artwork for mobile"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Optimize for mobile storage
            if self.is_termux:
                self.mobile_optimizer.optimize_image(file_path)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Could not download artwork: {e}")
            return False
    
    def search_and_download(self, track_info, playlist_name):
        """Search and download track with mobile optimizations"""
        search_query = track_info['search_query']
        safe_filename = self.sanitize_filename(search_query)
        
        # Create playlist directory
        playlist_dir = self.download_root / self.sanitize_filename(playlist_name)
        playlist_dir.mkdir(exist_ok=True)
        
        # Check if file already exists
        existing_files = list(playlist_dir.glob(f"{safe_filename}.*"))
        if existing_files:
            print(f"⏭️  Skipping (already exists): {safe_filename}")
            return True
        
        # Mobile optimization: Check battery and network
        if self.is_termux:
            if not self.mobile_optimizer.should_continue_download():
                print("🔋 Pausing download due to battery/network conditions")
                return False
        
        print(f"🔍 Searching: {search_query}")
        
        try:
            # Configure output path
            temp_output = str(self.temp_dir / f"{safe_filename}.%(ext)s")
            self.ydl_opts['outtmpl'] = temp_output
            
            # Download with progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        print(f"\r📥 Downloading: {percent:.1f}%", end='', flush=True)
                elif d['status'] == 'finished':
                    print(f"\n✅ Downloaded: {Path(d['filename']).name}")
            
            self.ydl_opts['progress_hooks'] = [progress_hook]
            
            # Search and download
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    # Search for best match
                    info = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                    if not info['entries']:
                        print(f"❌ No results found for: {search_query}")
                        return False
                    
                    video_info = info['entries'][0]
                    video_title = video_info.get('title', 'Unknown')
                    duration = video_info.get('duration', 0)
                    
                    # Verify duration similarity (within 30 seconds)
                    expected_duration = track_info['duration_ms'] / 1000
                    if abs(duration - expected_duration) > 30:
                        print(f"⚠️  Duration mismatch: Expected {expected_duration:.0f}s, got {duration:.0f}s")
                    
                    print(f"🎯 Found: {video_title}")
                    
                    # Download the video
                    ydl.download([video_info['webpage_url']])
                    
                except Exception as e:
                    print(f"❌ Download failed: {e}")
                    return False
            
            # Find downloaded file
            temp_files = list(self.temp_dir.glob(f"{safe_filename}.*"))
            if not temp_files:
                print(f"❌ Download file not found: {safe_filename}")
                return False
            
            downloaded_file = temp_files[0]
            
            # Download album artwork
            artwork_path = None
            if track_info['album_cover_url']:
                artwork_path = self.temp_dir / f"{safe_filename}_artwork.jpg"
                self.download_album_artwork(track_info['album_cover_url'], artwork_path)
            
            # Add metadata using audio manager
            success = self.audio_manager.embed_metadata(
                downloaded_file, track_info, artwork_path
            )
            
            if success:
                # Move to final location
                final_file = playlist_dir / f"{safe_filename}.mp3"
                downloaded_file.rename(final_file)
                
                # Cleanup temp files
                if artwork_path and artwork_path.exists():
                    artwork_path.unlink()
                
                # Send notification on mobile
                if self.is_termux:
                    self.termux_helper.send_notification(
                        f"Downloaded: {track_info['name']}",
                        f"By {', '.join(track_info['artists'])}"
                    )
                
                print(f"✅ Completed: {safe_filename}")
                return True
            else:
                print(f"⚠️  Metadata embedding failed: {safe_filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error downloading {search_query}: {e}")
            return False
    
    def download_playlist(self, playlist_url, max_concurrent=2):
        """Download entire playlist with mobile-optimized concurrency"""
        print(f"\n🎵 Starting playlist download...")
        
        # Get playlist information
        playlist_info, tracks = self.get_playlist_tracks(playlist_url)
        if not tracks:
            print("❌ No tracks found or error occurred")
            return
        
        print(f"\n📋 Playlist: {playlist_info['name']}")
        print(f"📊 Total tracks: {len(tracks)}")
        
        # Adjust concurrency for mobile
        if self.is_termux:
            max_concurrent = min(max_concurrent, 1)  # Single thread for mobile
        
        # Download tracks
        self.is_downloading = True
        successful = 0
        failed = 0
        
        start_time = time.time()
        
        for i, track in enumerate(tracks, 1):
            if not self.is_downloading:  # Check for interruption
                break
                
            print(f"\n[{i}/{len(tracks)}] Processing: {track['search_query']}")
            
            success = self.search_and_download(track, playlist_info['name'])
            
            if success:
                successful += 1
                self.completed_downloads.append(track)
            else:
                failed += 1
                self.failed_downloads.append(track)
            
            # Mobile optimization: Brief pause between downloads
            if self.is_termux and i < len(tracks):
                time.sleep(1)
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            eta = avg_time * (len(tracks) - i)
            
            print(f"📊 Progress: {i}/{len(tracks)} | ✅ {successful} | ❌ {failed} | ETA: {eta/60:.1f}m")
        
        # Final summary
        total_time = time.time() - start_time
        print(f"\n🎉 Download completed!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        
        # Send completion notification
        if self.is_termux:
            self.termux_helper.send_notification(
                "Playlist Download Complete",
                f"{successful}/{len(tracks)} tracks downloaded"
            )
        
        # Save failed downloads for retry
        if self.failed_downloads:
            failed_file = self.download_root / "failed_downloads.json"
            with open(failed_file, 'w') as f:
                json.dump(self.failed_downloads, f, indent=2)
            print(f"💾 Failed downloads saved to: {failed_file}")
    
    def retry_failed_downloads(self):
        """Retry failed downloads from previous session"""
        failed_file = self.download_root / "failed_downloads.json"
        
        if not failed_file.exists():
            print("📝 No failed downloads file found")
            return
        
        try:
            with open(failed_file, 'r') as f:
                failed_tracks = json.load(f)
            
            if not failed_tracks:
                print("📝 No failed downloads to retry")
                return
            
            print(f"🔄 Retrying {len(failed_tracks)} failed downloads...")
            
            self.failed_downloads = []
            successful = 0
            
            for track in failed_tracks:
                print(f"\n🔄 Retrying: {track['search_query']}")
                success = self.search_and_download(track, "RetryDownloads")
                
                if success:
                    successful += 1
                else:
                    self.failed_downloads.append(track)
            
            print(f"\n🔄 Retry completed: {successful}/{len(failed_tracks)} successful")
            
            # Update failed downloads file
            with open(failed_file, 'w') as f:
                json.dump(self.failed_downloads, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error retrying downloads: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        print(f"\n⚠️  Received signal {signum}, shutting down gracefully...")
        self.is_downloading = False
        
        if self.failed_downloads:
            failed_file = self.download_root / "failed_downloads.json"
            with open(failed_file, 'w') as f:
                json.dump(self.failed_downloads, f, indent=2)
            print(f"💾 Saved failed downloads to: {failed_file}")
        
        sys.exit(0)
    
    def interactive_mode(self):
        """Interactive mode for user-friendly operation"""
        print("\n🎵 Spotify to YouTube Downloader - Termux Edition")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Download playlist")
            print("2. Retry failed downloads")
            print("3. Check storage space")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                playlist_url = input("Enter Spotify playlist URL: ").strip()
                if playlist_url:
                    self.download_playlist(playlist_url)
                else:
                    print("❌ Invalid URL")
            
            elif choice == '2':
                self.retry_failed_downloads()
            
            elif choice == '3':
                self.check_storage_space()
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")

def main():
    """Main function"""
    try:
        downloader = TermuxSpotifyDownloader()
        
        if len(sys.argv) > 1:
            # Command line mode
            playlist_url = sys.argv[1]
            downloader.download_playlist(playlist_url)
        else:
            # Interactive mode
            downloader.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
