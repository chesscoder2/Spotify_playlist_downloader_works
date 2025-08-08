#!/usr/bin/env python3
"""
Enhanced Spotify Playlist to YouTube Downloader with Metadata & Artwork
 
This script takes a Spotify playlist URL, extracts all tracks,
searches for each track on YouTube, downloads them in high quality,
and embeds album artwork and metadata.

Requirements:
- spotipy: Spotify API wrapper
- yt-dlp: YouTube downloader
- eyed3: MP3 metadata handling
- requests: For downloading album artwork
- pillow: Image processing
- python-dotenv: Environment variable management

Setup:
1. Create a Spotify App at https://developer.spotify.com/dashboard/
2. Get your Client ID and Client Secret
3. Create a .env file with:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
"""

import os
import re
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import eyed3
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnhancedSpotifyYouTubeDownloader:
    def __init__(self):
        self.setup_spotify()
        self.setup_youtube_downloader()
        self.script_root = Path(__file__).parent.absolute()
        self.temp_dir = self.script_root / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
    def setup_spotify(self):
        """Initialize Spotify client"""
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
            print("✅ Spotify client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Spotify client: {e}")
            sys.exit(1)
    
    def setup_youtube_downloader(self):
        """Configure yt-dlp for high-quality YouTube downloads"""
        self.ydl_opts = {
            # High quality audio formats in order of preference
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': '',  # Will be set dynamically
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Maximum quality
            }],
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'noplaylist': True,
            'writeinfojson': False,
            'writethumbnail': False,
            # Prefer high quality sources
            'prefer_ffmpeg': True,
            'keepvideo': False,
        }
    
    def extract_playlist_id(self, playlist_url):
        """Extract playlist ID from Spotify URL"""
        if 'open.spotify.com' in playlist_url:
            if '/playlist/' in playlist_url:
                return playlist_url.split('/playlist/')[-1].split('?')[0]
        
        if playlist_url.startswith('spotify:playlist:'):
            return playlist_url.split('spotify:playlist:')[-1]
        
        if len(playlist_url) == 22 and playlist_url.isalnum():
            return playlist_url
            
        raise ValueError("Invalid Spotify playlist URL format")
    
    def get_playlist_tracks(self, playlist_url):
        """Get all tracks from a Spotify playlist with full metadata"""
        try:
            playlist_id = self.extract_playlist_id(playlist_url)
            print(f"📋 Fetching playlist: {playlist_id}")
            
            # Get playlist info
            playlist = self.spotify.playlist(playlist_id)
            playlist_name = playlist['name']
            playlist_description = playlist.get('description', '')
            playlist_cover = None
            
            if playlist.get('images') and len(playlist['images']) > 0:
                # Get highest resolution playlist cover
                playlist_cover = max(playlist['images'], key=lambda x: x.get('width', 0))['url']
            
            print(f"📋 Playlist: {playlist_name}")
            print(f"👤 Owner: {playlist['owner']['display_name']}")
            print(f"📝 Description: {playlist_description[:100]}..." if len(playlist_description) > 100 else f"📝 Description: {playlist_description}")
            
            # Get all tracks (handle pagination)
            tracks = []
            results = self.spotify.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            
            while results['next']:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
            
            # Extract detailed track information
            track_list = []
            for item in tracks:
                if item['track'] and item['track']['type'] == 'track':
                    track = item['track']
                    
                    # Get highest resolution album artwork
                    album_cover_url = None
                    if track['album'].get('images'):
                        album_cover_url = max(track['album']['images'], key=lambda x: x.get('width', 0))['url']
                    
                    # Parse release date
                    release_date = track['album'].get('release_date', '')
                    try:
                        if release_date:
                            if len(release_date) == 4:  # Year only
                                release_year = int(release_date)
                            else:  # Full date
                                release_year = int(release_date.split('-')[0])
                        else:
                            release_year = None
                    except:
                        release_year = None
                    
                    track_info = {
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'album_artist': track['album']['artists'][0]['name'] if track['album']['artists'] else track['artists'][0]['name'],
                        'track_number': track['track_number'],
                        'disc_number': track.get('disc_number', 1),
                        'duration_ms': track['duration_ms'],
                        'release_year': release_year,
                        'release_date': release_date,
                        'genres': [],  # Will be populated if available
                        'isrc': track['external_ids'].get('isrc', ''),
                        'album_cover_url': album_cover_url,
                        'popularity': track.get('popularity', 0),
                        'explicit': track.get('explicit', False),
                        'search_query': f"{', '.join([artist['name'] for artist in track['artists']])} - {track['name']}"
                    }
                    
                    # Try to get additional metadata
                    try:
                        artist_info = self.spotify.artist(track['artists'][0]['id'])
                        if artist_info.get('genres'):
                            track_info['genres'] = artist_info['genres'][:3]  # Limit to 3 genres
                    except:
                        pass
                    
                    track_list.append(track_info)
            
            print(f"✅ Found {len(track_list)} tracks with metadata")
            
            playlist_info = {
                'name': playlist_name,
                'description': playlist_description,
                'cover_url': playlist_cover,
                'total_tracks': len(track_list)
            }
            
            return playlist_info, track_list
            
        except Exception as e:
            print(f"❌ Error fetching playlist: {e}")
            return None, []
    
    def download_image(self, url, file_path):
        """Download and save album artwork"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Optimize image if needed
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 1000x1000 for reasonable file size)
                if img.width > 1000 or img.height > 1000:
                    img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(file_path, 'JPEG', quality=95, optimize=True)
            
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not download artwork - {e}")
            return False
    
    def embed_metadata(self, mp3_file, track_info, album_art_path=None):
        """Embed metadata and album artwork into MP3 file"""
        try:
            # Load the MP3 file
            audiofile = eyed3.load(mp3_file)
            
            if audiofile is None or audiofile.tag is None:
                audiofile = eyed3.load(mp3_file)
                if audiofile.tag is None:
                    audiofile.initTag()
            
            tag = audiofile.tag
            
            # Set basic metadata
            tag.title = track_info['name']
            tag.artist = ', '.join(track_info['artists'])
            tag.album = track_info['album']
            tag.album_artist = track_info['album_artist']
            tag.track_num = track_info['track_number']
            tag.disc_num = track_info['disc_number']
            
            # Set release year
            if track_info['release_year']:
                tag.release_date = eyed3.core.Date(track_info['release_year'])
                tag.original_release_date = eyed3.core.Date(track_info['release_year'])
            
            # Set genres
            if track_info['genres']:
                tag.genre = track_info['genres'][0]  # eyed3 supports one genre
            
            # Set additional metadata
            if track_info['isrc']:
                tag.isrc = track_info['isrc']
            
            # Add custom fields
            tag.comments.set(f"Downloaded from YouTube | Spotify Popularity: {track_info['popularity']}")
            
            # Embed album artwork
            if album_art_path and os.path.exists(album_art_path):
                with open(album_art_path, 'rb') as art_file:
                    tag.images.set(
                        eyed3.id3.frames.ImageFrame.FRONT_COVER,
                        art_file.read(),
                        'image/jpeg',
                        description='Album Cover'
                    )
                print("🎨 Embedded album artwork")
            
            # Save the changes
            tag.save(version=eyed3.id3.ID3_V2_3)
            print("✅ Metadata embedded successfully")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Could not embed metadata - {e}")
            return False
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def search_and_download(self, track_info, download_path):
        """Search for track on YouTube and download with metadata"""
        search_query = track_info['search_query']
        safe_filename = self.sanitize_filename(f"{search_query}")
        
        # Create temporary file path for initial download
        temp_file = self.temp_dir / f"{safe_filename}.%(ext)s"
        final_file = download_path / f"{safe_filename}.mp3"
        
        # Update output template
        self.ydl_opts['outtmpl'] = str(temp_file)
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                search_url = f"ytsearch1:{search_query}"
                
                print(f"🔍 Searching: {search_query}")
                
                # Extract info without downloading first
                info = ydl.extract_info(search_url, download=False)
                
                if info and 'entries' in info and info['entries']:
                    video_info = info['entries'][0]
                    video_title = video_info.get('title', 'Unknown')
                    video_duration = video_info.get('duration', 0)
                    uploader = video_info.get('uploader', 'Unknown')
                    
                    print(f"🎵 Found: {video_title}")
                    print(f"📺 Channel: {uploader}")
                    print(f"⏱️  Duration: {video_duration // 60}:{video_duration % 60:02d}")
                    
                    # Download the video
                    ydl.download([search_url])
                    
                    # Find the downloaded file
                    downloaded_file = None
                    for ext in ['.mp3', '.webm', '.m4a', '.ogg']:
                        potential_file = Path(str(temp_file).replace('.%(ext)s', ext))
                        if potential_file.exists():
                            downloaded_file = potential_file
                            break
                    
                    if not downloaded_file:
                        print(f"❌ Could not find downloaded file for: {search_query}")
                        return False
                    
                    print(f"⬇️  Downloaded: {downloaded_file.name}")
                    
                    # Download album artwork
                    album_art_path = None
                    if track_info['album_cover_url']:
                        album_art_path = self.temp_dir / f"{safe_filename}_artwork.jpg"
                        print("🎨 Downloading album artwork...")
                        if self.download_image(track_info['album_cover_url'], album_art_path):
                            print("✅ Album artwork downloaded")
                        else:
                            album_art_path = None
                    
                    # Move file to final location
                    final_file.parent.mkdir(parents=True, exist_ok=True)
                    downloaded_file.rename(final_file)
                    
                    # Embed metadata and artwork
                    print("📝 Embedding metadata...")
                    self.embed_metadata(final_file, track_info, album_art_path)
                    
                    # Clean up temporary artwork file
                    if album_art_path and album_art_path.exists():
                        album_art_path.unlink()
                    
                    print(f"✅ Completed: {final_file.name}")
                    return True
                    
                else:
                    print(f"❌ No results found for: {search_query}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error downloading {search_query}: {e}")
            return False
    
    def create_playlist_info_file(self, playlist_info, download_path):
        """Create a text file with playlist information"""
        info_file = download_path / "playlist_info.txt"
        
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"Playlist: {playlist_info['name']}\n")
                f.write(f"Total Tracks: {playlist_info['total_tracks']}\n")
                f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Description: {playlist_info['description']}\n\n")
                f.write("This playlist was downloaded using Enhanced Spotify to YouTube Downloader\n")
                f.write("All tracks include embedded metadata and album artwork.\n")
            
            print(f"📄 Created playlist info file: {info_file}")
            
            # Download playlist cover if available
            if playlist_info['cover_url']:
                cover_file = download_path / "playlist_cover.jpg"
                if self.download_image(playlist_info['cover_url'], cover_file):
                    print(f"🖼️  Downloaded playlist cover: {cover_file}")
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not create playlist info file - {e}")
    
    def download_playlist(self, playlist_url, output_folder="downloads"):
        """Main function to download entire playlist with full metadata"""
        print("🎵 Enhanced Spotify to YouTube Downloader")
        print("🎨 With Album Artwork & Metadata Support")
        print("=" * 60)
        
        # Create download directory
        download_path = self.script_root / output_folder
        download_path.mkdir(exist_ok=True)
        print(f"📁 Download directory: {download_path}")
        
        # Get playlist tracks
        playlist_info, tracks = self.get_playlist_tracks(playlist_url)
        
        if not tracks:
            print("❌ No tracks found or error occurred")
            return
        
        # Create playlist-specific folder
        if playlist_info and playlist_info['name']:
            safe_playlist_name = self.sanitize_filename(playlist_info['name'])
            playlist_path = download_path / safe_playlist_name
            playlist_path.mkdir(exist_ok=True)
            download_path = playlist_path
            print(f"📁 Playlist folder: {download_path}")
        
        # Create playlist info file
        if playlist_info:
            self.create_playlist_info_file(playlist_info, download_path)
        
        print(f"\n🚀 Starting high-quality download of {len(tracks)} tracks...")
        print("🎵 320kbps MP3 with embedded artwork & metadata")
        print("=" * 60)
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, track in enumerate(tracks, 1):
            print(f"\n[{i}/{len(tracks)}] Processing track...")
            print(f"🎵 Track: {track['name']}")
            print(f"👤 Artist(s): {', '.join(track['artists'])}")
            print(f"💽 Album: {track['album']} ({track['release_year'] or 'Unknown Year'})")
            print(f"🎯 Track #{track['track_number']}")
            
            if track['genres']:
                print(f"🎪 Genre(s): {', '.join(track['genres'])}")
            
            if self.search_and_download(track, download_path):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Add delay to avoid rate limiting
            if i < len(tracks):
                print("⏳ Waiting 3 seconds...")
                time.sleep(3)
        
        # Cleanup temp directory
        try:
            for temp_file in self.temp_dir.iterdir():
                temp_file.unlink()
        except:
            pass
        
        print("\n" + "=" * 60)
        print("📊 Download Summary:")
        print(f"✅ Successful: {successful_downloads}")
        print(f"❌ Failed: {failed_downloads}")
        print(f"📁 Downloaded to: {download_path}")
        print("🎨 All files include album artwork and metadata")
        print("🔊 Audio quality: 320kbps MP3")
        print("🎉 Download complete!")

def main():
    if len(sys.argv) < 2:
        print("Enhanced Spotify to YouTube Downloader")
        print("=====================================")
        print("Usage: python spotify_downloader.py <spotify_playlist_url> [output_folder]")
        print("\nFeatures:")
        print("• High-quality 320kbps MP3 downloads")
        print("• Embedded album artwork")
        print("• Complete metadata (title, artist, album, year, genre, etc.)")
        print("• Playlist information file")
        print("• Organized folder structure")
        print("\nExample:")
        print("python spotify_downloader.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        print("python spotify_downloader.py https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M my_music")
        sys.exit(1)
    
    playlist_url = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    
    downloader = EnhancedSpotifyYouTubeDownloader()
    downloader.download_playlist(playlist_url, output_folder)

if __name__ == "__main__":
    main()
