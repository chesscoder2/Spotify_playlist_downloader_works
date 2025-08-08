#!/bin/bash
# Termux Launcher Script for Spotify YouTube Downloader

echo "🎵 Starting Spotify YouTube Downloader for Termux..."
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your Spotify credentials:"
    echo "cp .env.example .env"
    echo "nano .env"
    echo ""
    echo "Get credentials from: https://developer.spotify.com/dashboard/"
    exit 1
fi

# Check if in Termux
if [[ "$PREFIX" == *"com.termux"* ]]; then
    echo "📱 Termux environment detected"
    
    # Setup storage if needed
    if [ ! -d "/storage/emulated/0" ]; then
        echo "🔐 Setting up storage access..."
        termux-setup-storage
    fi
    
    # Check Termux:API
    if command -v termux-notification &> /dev/null; then
        echo "✅ Termux:API available - full features enabled"
    else
        echo "⚠️  Termux:API not found - limited features"
        echo "   Install from F-Droid for notifications and system integration"
    fi
else
    echo "💻 Standard environment detected"
fi

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install --quiet spotipy yt-dlp mutagen pillow requests python-dotenv psutil tqdm colorama

# Run the downloader
echo "🚀 Starting downloader..."
python main.py "$@"