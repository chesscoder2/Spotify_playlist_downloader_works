# 🌐 Spotify YouTube Downloader - Termux Web Interface Guide

Complete guide to run the Spotify YouTube Downloader on Termux with a web interface that can be shared via URL.

## 📱 Prerequisites

### 1. Install Termux
- **Recommended**: Download from [F-Droid](https://f-droid.org/packages/com.termux/) (more stable)
- **Alternative**: Google Play Store (may have limitations)

### 2. Install Termux:API (Optional but Recommended)
- Download from [F-Droid](https://f-droid.org/packages/com.termux.api/)
- Enables notifications and Android system integration

### 3. Get Spotify API Credentials
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in app details (any name/description)
5. Copy your **Client ID** and **Client Secret**

## 🚀 Quick Setup

### 1. Download and Setup
```bash
# Open Termux and run:
pkg update && pkg install git curl
git clone <your-repo-url>
cd spotify-youtube-downloader

# Run the web setup script
chmod +x termux_web_setup.sh
./termux_web_setup.sh
```

### 2. Configure Credentials
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your Spotify credentials
nano .env
```

In the `.env` file, replace with your actual credentials:
```env
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

### 3. Start the Web Interface
```bash
# Start the web server
./start_web.sh
```

You'll see output like:
```
🎵 Starting Spotify YouTube Downloader Web Interface...
======================================================
🌐 Starting web server...
📱 Local access: http://localhost:5000
🔗 Network access: http://192.168.1.100:5000
📡 Share this URL with others on the same network
```

## 🔗 Sharing Your URL

### Option 1: Local Network Sharing
- Anyone on the same WiFi can access your server
- Share the network URL shown (e.g., `http://192.168.1.100:5000`)
- Works great for home/office use

### Option 2: Public URL (Internet Access)
For sharing with anyone on the internet:

```bash
# Setup public tunnel
./setup_public_url.sh

# In another Termux session, start the tunnel
cloudflared tunnel --url http://localhost:5000
```

You'll get a public URL like: `https://random-words-1234.trycloudflare.com`

## 🎵 Using the Web Interface

### Features Available:
1. **Search Public Playlists**: Find playlists by keywords
2. **Direct URL Input**: Paste Spotify playlist URLs
3. **Download Limits**: Set max songs per download (1-300)
4. **Real-time Progress**: Watch download progress live
5. **ZIP Downloads**: Get all songs in one ZIP file

### Supported Playlist Types:
- ✅ Public user playlists
- ✅ Spotify's editorial playlists
- ❌ Private playlists (not accessible via API)
- ❌ Some auto-generated playlists

### Audio Quality:
- **First Choice**: FLAC (lossless)
- **Fallback**: High-quality Opus/WebM
- **Standard**: 320kbps MP3
- **Includes**: Complete metadata and album artwork

## 🛠️ Advanced Usage

### Command Line Interface
For direct terminal use:
```bash
# Interactive mode
python main.py

# Direct playlist download
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWFJp05Sa8"
```

### Batch Processing
```bash
# Create playlist file
echo "https://open.spotify.com/playlist/..." >> playlists.txt
echo "https://open.spotify.com/playlist/..." >> playlists.txt

# Process all playlists
while read url; do python main.py "$url"; done < playlists.txt
```

### Customizing Settings
Edit `.env` file for custom settings:
```env
# Audio quality (bitrate for MP3 fallback)
AUDIO_QUALITY=320

# Maximum image size for album art
IMAGE_MAX_SIZE=800

# Download concurrency (keep at 1 for mobile)
MAX_CONCURRENT_DOWNLOADS=1
```

## 📁 File Locations

### Downloaded Music
- **Location**: `/storage/emulated/0/Music/SpotifyDownloads/`
- **Format**: `Artist - Song Title.mp3` (or .flac)
- **ZIP Files**: Downloaded via web interface to `downloads/` folder

### Temporary Files
- **Location**: `~/downloads/temp_spotify/`
- **Auto-cleanup**: Yes, after successful download

## 🚨 Troubleshooting

### "Permission Denied" Error
```bash
# Grant storage permission
termux-setup-storage
# Allow when Android prompts for permission
```

### "Spotify API Error"
- Check your Client ID and Secret in `.env`
- Ensure the Spotify app is properly configured
- Try a different playlist (some are private/restricted)

### "Can't Find Playlist"
- Make sure the playlist is public
- Use the search feature to find working playlists
- Some auto-generated playlists aren't accessible

### Web Interface Not Loading
```bash
# Check if the server is running
./start_web.sh

# Check firewall (if on restricted network)
# Make sure port 5000 is accessible
```

### Low Memory Issues
- Close other apps while downloading
- Use smaller download limits (50-100 songs)
- The app will automatically pause on low memory

## 🔒 Security Notes

### Local Network
- Only people on your WiFi can access the local URL
- No internet exposure unless you use tunneling

### Public Tunnels
- Anyone with the tunnel URL can access your downloader
- Tunnel URLs are temporary and change each session
- Don't share tunnel URLs publicly if you want privacy

### API Keys
- Keep your Spotify credentials private
- Don't share your `.env` file
- Rotate keys if compromised

## 📊 Performance Tips

### For Better Downloads:
1. **Stable WiFi**: Use strong, stable internet connection
2. **Battery**: Keep device plugged in for large downloads
3. **Storage**: Ensure sufficient free space
4. **Background**: Avoid running too many other apps

### Optimal Settings:
- **Small playlists**: 1-50 songs work fastest
- **Medium playlists**: 50-150 songs (good balance)
- **Large playlists**: 150-300 songs (may take time)

## 🎯 Use Cases

### Personal Use
- Download your Spotify playlists for offline listening
- Backup your music collection
- Convert Spotify playlists to local files

### Sharing with Friends
- Set up for parties or events
- Let friends download playlists they like
- Create a shared music downloading station

### Small Groups
- Family music sharing
- Small office or studio use
- Study group playlist sharing

## 📞 Getting Help

### Common Resources
- Check this guide first
- Look at error messages carefully
- Try with a smaller, simpler playlist first

### Still Need Help?
1. Copy the exact error message
2. Note what you were trying to do
3. Check if the playlist is public and accessible
4. Try the command line version to see detailed errors

## 🎉 Success Tips

1. **Start Small**: Try a small public playlist first
2. **Test Local**: Make sure the web interface works locally before sharing
3. **Check Credentials**: Verify Spotify API access works
4. **Stable Network**: Use reliable WiFi for downloading
5. **Be Patient**: Large playlists take time, especially on mobile

---

**Enjoy your high-quality music downloads! 🎵**