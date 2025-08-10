#!/usr/bin/env python3
"""
Web interface for Spotify to YouTube downloader
Allows users to download playlists as zip files
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import zipfile
import tempfile
import threading
import time
from datetime import datetime
import json
import shutil
import re
import sys
import random
sys.path.append('.')
from main import TermuxSpotifyDownloader
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

app = Flask(__name__)
app.secret_key = 'spotify_downloader_secret_key_2025'

# Global storage for download status
download_status_dict = {}

class WebDownloader:
    def __init__(self):
        self.downloader = TermuxSpotifyDownloader()
        self.user_agents = [
            'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
            'com.google.android.youtube/19.08.35 (Linux; U; Android 12) gzip',
            'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'com.google.android.youtube.tv/2.12.08 (Linux; U; Android 9)',
        ]
        
    def download_single_track(self, search_query, track_info, output_dir):
        """Download a single track using yt-dlp with advanced bot detection bypass"""
        try:
            # Sanitize filename
            safe_name = re.sub(r'[^\w\s-]', '', f"{track_info['artist']} - {track_info['name']}")
            safe_name = re.sub(r'[-\s]+', '-', safe_name).strip('-')
            
            # Advanced yt-dlp options with stronger bot detection bypass
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'outtmpl': os.path.join(output_dir, f'{safe_name}.%(ext)s'),
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '320K',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
                
                # Comprehensive bot detection bypass
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_music', 'android', 'ios', 'web', 'mweb'],
                        'player_skip': ['webpage', 'configs', 'js'],
                        'skip': ['hls', 'dash'],
                        'po_token': None,
                        'visitor_data': None,
                    }
                },
                
                # Multiple user agents rotation
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Origin': 'https://www.youtube.com',
                    'Referer': 'https://www.youtube.com/',
                    'X-YouTube-Client-Name': '3',
                    'X-YouTube-Client-Version': '19.09.37',
                },
                
                # Enhanced retry and timeout settings
                'retries': 5,
                'fragment_retries': 5,
                'file_access_retries': 3,
                'extractor_retries': 3,
                'socket_timeout': 30,
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                'sleep_interval_requests': 1,
                
                # Additional bypass options
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'force_json': False,
                'simulate': False,
                'skip_download': False,
                'prefer_insecure': False,
                'proxy': None,
                
                # Disable problematic features
                'youtube_include_dash_manifest': False,
                'mark_watched': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }
            
            # Try multiple bypass strategies
            bypass_strategies = [
                # Strategy 1: Android Music client
                {**ydl_opts, 'extractor_args': {'youtube': {
                    'player_client': ['android_music'],
                    'player_skip': ['webpage', 'configs', 'js']
                }}},
                # Strategy 2: iOS client
                {**ydl_opts, 'extractor_args': {'youtube': {
                    'player_client': ['ios'],
                    'player_skip': ['webpage']
                }}, 'http_headers': {
                    'User-Agent': 'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
                    'X-YouTube-Client-Name': '5',
                    'X-YouTube-Client-Version': '19.09.3',
                }},
                # Strategy 3: Web client with cookies
                {**ydl_opts, 'extractor_args': {'youtube': {
                    'player_client': ['web'],
                    'player_skip': ['configs']
                }}, 'cookiefile': None},
                # Strategy 4: Android TV client
                {**ydl_opts, 'extractor_args': {'youtube': {
                    'player_client': ['android_embedded'],
                }}, 'http_headers': {
                    'User-Agent': 'com.google.android.youtube.tv/2.12.08 (Linux; U; Android 9)',
                }},
            ]
            
            for i, strategy in enumerate(bypass_strategies):
                try:
                    print(f"🔄 Trying bypass strategy {i+1}/4...")
                    with yt_dlp.YoutubeDL(strategy) as ydl:
                        # Search and download
                        search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                        if search_results and 'entries' in search_results and search_results['entries']:
                            video_info = search_results['entries'][0]
                            ydl.download([video_info['webpage_url']])
                            
                            # Find the downloaded file
                            for file in os.listdir(output_dir):
                                if safe_name in file and (file.endswith('.mp3') or file.endswith('.m4a')):
                                    print(f"✅ Success with strategy {i+1}")
                                    return os.path.join(output_dir, file)
                except Exception as e:
                    print(f"⚠️ Strategy {i+1} failed: {str(e)[:100]}...")
                    if i < len(bypass_strategies) - 1:
                        time.sleep(2)  # Wait before trying next strategy
                    continue
                            
        except Exception as e:
            print(f"Error downloading {track_info['name']}: {e}")
            
        return None
    
    def embed_track_metadata(self, audio_file, track_info):
        """Embed metadata including album cover into audio file"""
        try:
            import mutagen
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TPE2, TRCK, TDRC, TCON
            import requests
            
            # Load the audio file
            audio = MP3(audio_file, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()
            
            tags = audio.tags
            tags.clear()
            
            # Add basic metadata
            tags.add(TIT2(encoding=3, text=track_info['name']))
            tags.add(TPE1(encoding=3, text=track_info['artist']))
            tags.add(TALB(encoding=3, text=track_info['album']))
            tags.add(TPE2(encoding=3, text=track_info['artist']))
            
            # Try to get album cover from Spotify
            try:
                # Get track details from Spotify to find album cover
                search_results = self.downloader.spotify.search(
                    q=f"track:{track_info['name']} artist:{track_info['artist']}", 
                    type='track', 
                    limit=1
                )
                
                if search_results['tracks']['items']:
                    spotify_track = search_results['tracks']['items'][0]
                    if spotify_track['album']['images']:
                        # Get highest resolution image
                        album_cover_url = spotify_track['album']['images'][0]['url']
                        
                        # Download album cover
                        response = requests.get(album_cover_url, timeout=10)
                        if response.status_code == 200:
                            tags.add(APIC(
                                encoding=3,
                                mime='image/jpeg',
                                type=3,  # Cover (front)
                                desc='Album Cover',
                                data=response.content
                            ))
                            print(f"✅ Added album cover for {track_info['name']}")
            except Exception as e:
                print(f"⚠️ Could not add album cover: {e}")
            
            # Save the metadata
            audio.save(v2_version=3)
            print(f"✅ Metadata embedded for {track_info['name']}")
            
        except Exception as e:
            print(f"❌ Error embedding metadata: {e}")
        
    def download_playlist_web(self, playlist_url, max_songs=300, download_id=None):
        """Download playlist with web progress tracking"""
        try:
            # Update status
            download_status_dict[download_id] = {
                'status': 'initializing',
                'progress': 0,
                'current_song': '',
                'downloaded': 0,
                'total': 0,
                'error': None,
                'zip_file': None,
                'started_at': datetime.now().isoformat()
            }
            
            # Extract playlist ID
            if 'playlist/' in playlist_url:
                playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
            else:
                raise ValueError("Invalid playlist URL")
                
            download_status_dict[download_id]['status'] = 'fetching_playlist'
            
            # Get playlist tracks
            playlist_data = self.downloader.spotify.playlist(playlist_id)
            tracks = []
            
            # Get tracks from playlist
            results = playlist_data['tracks']
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        track = item['track']
                        track_info = {
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'duration': track['duration_ms'],
                            'spotify_url': track['external_urls']['spotify']
                        }
                        tracks.append(track_info)
                        
                if results['next']:
                    results = self.downloader.spotify.next(results)
                else:
                    results = None
            
            if not tracks:
                raise ValueError("No tracks found or playlist not accessible")
                
            # Limit tracks
            tracks = tracks[:max_songs]
            
            download_status_dict[download_id].update({
                'status': 'downloading',
                'total': len(tracks),
                'playlist_name': playlist_data.get('name', 'Unknown Playlist')
            })
            
            # Create temp directory for this download
            temp_dir = tempfile.mkdtemp(prefix=f'spotify_download_{download_id}_')
            downloaded_files = []
            
            for i, track in enumerate(tracks):
                try:
                    download_status_dict[download_id].update({
                        'current_song': f"{track['name']} - {track['artist']}",
                        'progress': int((i / len(tracks)) * 100)
                    })
                    
                    # Add random delay between downloads to avoid rate limiting
                    if i > 0:
                        delay = random.uniform(1, 3)
                        print(f"💤 Waiting {delay:.1f}s to avoid detection...")
                        time.sleep(delay)
                    
                    # Download the track using YouTube search
                    search_query = f"{track['artist']} {track['name']}"
                    filename = self.download_single_track(search_query, track, temp_dir)
                    if filename and os.path.exists(filename):
                        # Embed metadata and album cover
                        self.embed_track_metadata(filename, track)
                        downloaded_files.append(filename)
                        download_status_dict[download_id]['downloaded'] = len(downloaded_files)
                        
                except Exception as e:
                    print(f"Error downloading {track['name']}: {e}")
                    continue
            
            # Create zip file
            download_status_dict[download_id]['status'] = 'creating_zip'
            
            zip_filename = f"spotify_playlist_{playlist_id}_{int(time.time())}.zip"
            zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in downloaded_files:
                    if os.path.exists(file_path):
                        # Use just the filename in the zip
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
            
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            download_status_dict[download_id].update({
                'status': 'completed',
                'progress': 100,
                'zip_file': zip_path,
                'completed_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            download_status_dict[download_id] = {
                'status': 'error',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            }

web_downloader = WebDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_download', methods=['POST'])
def start_download():
    playlist_url = request.form.get('playlist_url', '').strip()
    max_songs = int(request.form.get('max_songs', 300))
    
    if not playlist_url:
        flash('Please enter a valid Spotify playlist URL')
        return redirect(url_for('index'))
    
    if not ('open.spotify.com/playlist/' in playlist_url):
        flash('Please enter a valid Spotify playlist URL')
        return redirect(url_for('index'))
    
    # Generate download ID
    download_id = f"download_{int(time.time())}_{hash(playlist_url) % 10000}"
    
    # Start download in background thread
    thread = threading.Thread(
        target=web_downloader.download_playlist_web,
        args=(playlist_url, max_songs, download_id)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('download_status', download_id=download_id))

@app.route('/status/<download_id>')
def download_status(download_id):
    return render_template('status.html', download_id=download_id)

@app.route('/api/status/<download_id>')
def get_download_status(download_id):
    status = download_status_dict.get(download_id, {
        'status': 'not_found',
        'error': 'Download not found'
    })
    return jsonify(status)

@app.route('/download/<download_id>')
def download_file(download_id):
    status = download_status_dict.get(download_id, {})
    
    if status.get('status') != 'completed' or not status.get('zip_file'):
        flash('Download not ready or not found')
        return redirect(url_for('index'))
    
    zip_path = status['zip_file']
    if not os.path.exists(zip_path):
        flash('Download file not found')
        return redirect(url_for('index'))
    
    playlist_name = status.get('playlist_name', 'playlist')
    safe_name = "".join(c for c in playlist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_name}.zip"
    
    return send_file(zip_path, as_attachment=True, download_name=filename)

@app.route('/search_playlists')
def search_playlists():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'status': 'error', 'message': 'Search query is required'})
    
    try:
        # Search for playlists
        results = web_downloader.downloader.spotify.search(q=query, type='playlist', limit=20)
        
        playlists = []
        if results and 'playlists' in results and results['playlists']['items']:
            for playlist in results['playlists']['items']:
                if playlist and 'id' in playlist:
                    try:
                        # Test if we can access this playlist
                        test_playlist = web_downloader.downloader.spotify.playlist(
                            playlist['id'], 
                            fields="name,tracks.total,owner.display_name,images"
                        )
                        
                        if test_playlist['tracks']['total'] > 0:
                            image_url = None
                            if test_playlist.get('images') and len(test_playlist['images']) > 0:
                                image_url = test_playlist['images'][0]['url']
                            
                            playlists.append({
                                'id': playlist['id'],
                                'name': test_playlist['name'],
                                'tracks': test_playlist['tracks']['total'],
                                'owner': test_playlist.get('owner', {}).get('display_name', 'Unknown'),
                                'url': f"https://open.spotify.com/playlist/{playlist['id']}",
                                'image': image_url
                            })
                            
                    except Exception:
                        continue  # Skip inaccessible playlists
        
        return jsonify({
            'status': 'success',
            'playlists': playlists,
            'count': len(playlists)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Search failed: {str(e)}'})

@app.route('/test_connection')
def test_connection():
    try:
        # Test Spotify connection
        results = web_downloader.downloader.spotify.search(q='test', type='artist', limit=1)
        return jsonify({'status': 'success', 'message': 'Spotify API connected successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Connection failed: {str(e)}'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)