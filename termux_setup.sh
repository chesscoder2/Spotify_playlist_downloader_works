#!/bin/bash
# Termux Setup Script for Spotify YouTube Downloader
# This script installs all required dependencies for Termux

echo "🎵 Setting up Spotify YouTube Downloader for Termux..."
echo "=================================================="

# Update package repository
echo "📦 Updating package repository..."
pkg update -y

# Install Python and pip
echo "🐍 Installing Python..."
pkg install -y python python-pip

# Install essential packages
echo "🔧 Installing essential packages..."
pkg install -y git curl wget

# Install ffmpeg for audio processing
echo "🎧 Installing FFmpeg..."
pkg install -y ffmpeg

# Install required system libraries
echo "📚 Installing system libraries..."
pkg install -y libjpeg-turbo libpng zlib openssl libffi

# Install Termux:API if not already installed
echo "📱 Checking Termux:API..."
if ! command -v termux-notification &> /dev/null; then
    echo "⚠️  Termux:API not found. Please install it from F-Droid or Google Play"
    echo "   This enables notifications and other Android features"
fi

# Setup storage access
echo "💾 Setting up storage access..."
echo "   Please allow storage permission when prompted"
termux-setup-storage

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install --upgrade pip

# Install main dependencies
pip install spotipy yt-dlp mutagen pillow requests python-dotenv psutil

# Additional useful packages
pip install tqdm colorama

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/storage/music/SpotifyDownloads
mkdir -p ~/downloads/temp_spotify

# Set up environment
echo "🔧 Setting up environment..."
cat > ~/.spotify_downloader_env << 'EOF'
# Spotify YouTube Downloader Environment
export SPOTIFY_DOWNLOADS_DIR="$HOME/storage/music/SpotifyDownloads"
export TEMP_DIR="$HOME/downloads/temp_spotify"
export PYTHONHASHSEED=0
export MALLOC_TRIM_THRESHOLD_=100000
EOF

# Add to .bashrc if it exists
if [ -f ~/.bashrc ]; then
    echo "source ~/.spotify_downloader_env" >> ~/.bashrc
fi

# Create .env template
echo "📝 Creating .env template..."
cat > .env.example << 'EOF'
# Spotify API Credentials
# Get these from: https://developer.spotify.com/dashboard/
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Optional: Download settings
MAX_CONCURRENT_DOWNLOADS=1
AUDIO_QUALITY=320
IMAGE_MAX_SIZE=800
EOF

# Set permissions
chmod +x spotify_youtube_downloader.py

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your .env file with Spotify credentials:"
echo "   cp .env.example .env"
echo "   nano .env  # Edit with your credentials"
echo ""
echo "2. Run the downloader:"
echo "   python spotify_youtube_downloader.py"
echo ""
echo "🔗 Get Spotify credentials:"
echo "   https://developer.spotify.com/dashboard/"
echo ""
echo "📱 For full Android integration, install Termux:API:"
echo "   https://f-droid.org/packages/com.termux.api/"
echo ""
echo "🎵 Happy downloading!"
