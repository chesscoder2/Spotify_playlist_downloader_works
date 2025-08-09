#!/bin/bash
# Termux Web Interface Setup Script for Spotify YouTube Downloader
# This script sets up the web interface with a shareable URL

echo "🌐 Setting up Spotify YouTube Downloader Web Interface for Termux..."
echo "================================================================="

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

# Install Python dependencies for web interface
echo "🐍 Installing Python packages..."
pip install --upgrade pip

# Install main dependencies including Flask for web interface
pip install spotipy yt-dlp mutagen pillow requests python-dotenv psutil tqdm colorama flask

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/storage/music/SpotifyDownloads
mkdir -p ~/downloads/temp_spotify
mkdir -p ~/downloads

# Set up environment for web interface
echo "🔧 Setting up environment..."
cat > ~/.spotify_downloader_env << 'EOF'
# Spotify YouTube Downloader Environment
export SPOTIFY_DOWNLOADS_DIR="$HOME/storage/music/SpotifyDownloads"
export TEMP_DIR="$HOME/downloads/temp_spotify"
export PYTHONHASHSEED=0
export MALLOC_TRIM_THRESHOLD_=100000
export FLASK_ENV=production
export FLASK_DEBUG=0
EOF

# Add to .bashrc if it exists
if [ -f ~/.bashrc ]; then
    echo "source ~/.spotify_downloader_env" >> ~/.bashrc
fi

# Create .env template with web settings
echo "📝 Creating .env template..."
cat > .env.example << 'EOF'
# Spotify API Credentials
# Get these from: https://developer.spotify.com/dashboard/
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Web Interface Settings
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Optional: Download settings
MAX_CONCURRENT_DOWNLOADS=1
AUDIO_QUALITY=320
IMAGE_MAX_SIZE=800
EOF

# Create web startup script
echo "🌐 Creating web startup script..."
cat > start_web.sh << 'EOF'
#!/bin/bash
# Startup script for Spotify Downloader Web Interface

echo "🎵 Starting Spotify YouTube Downloader Web Interface..."
echo "======================================================"

# Load environment
source ~/.spotify_downloader_env

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy and edit .env.example:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Get local IP address
LOCAL_IP=$(ip route get 1.1.1.1 | grep -oP 'src \K[^ ]+')

echo "🌐 Starting web server..."
echo "📱 Local access: http://localhost:5000"
echo "🔗 Network access: http://$LOCAL_IP:5000"
echo "📡 Share this URL with others on the same network"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the web application
python web_app.py
EOF

# Create tunnel setup script for public URL
echo "🚇 Creating tunnel setup script..."
cat > setup_public_url.sh << 'EOF'
#!/bin/bash
# Setup public URL access using ngrok or similar

echo "🌐 Setting up Public URL Access..."
echo "================================="

echo "Installing cloudflared for public tunnels..."
# Download cloudflared for Android ARM64
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" ]]; then
    echo "📥 Downloading cloudflared for ARM64..."
    wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
elif [[ "$ARCH" == "armv7l" ]]; then
    echo "📥 Downloading cloudflared for ARM..."
    wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

chmod +x cloudflared
mv cloudflared $PREFIX/bin/

echo "✅ Cloudflared installed successfully!"
echo ""
echo "📋 To create a public tunnel:"
echo "1. Start the web interface: ./start_web.sh"
echo "2. In another terminal, run: cloudflared tunnel --url http://localhost:5000"
echo "3. Copy the public URL shown and share it"
echo ""
echo "🔒 Note: The tunnel will stay active while the command is running"
EOF

# Set permissions
chmod +x start_web.sh
chmod +x setup_public_url.sh
chmod +x termux_setup.sh

echo ""
echo "✅ Web Interface Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your .env file with Spotify credentials:"
echo "   cp .env.example .env"
echo "   nano .env  # Edit with your credentials"
echo ""
echo "2. Start the web interface:"
echo "   ./start_web.sh"
echo ""
echo "3. For public URL access (optional):"
echo "   ./setup_public_url.sh"
echo ""
echo "🔗 Get Spotify credentials:"
echo "   https://developer.spotify.com/dashboard/"
echo ""
echo "🌐 Web Interface Features:"
echo "   - Search public playlists"
echo "   - Download as ZIP files"
echo "   - Real-time progress tracking"
echo "   - Mobile-friendly interface"
echo ""
echo "📱 For full Android integration, install Termux:API:"
echo "   https://f-droid.org/packages/com.termux.api/"
echo ""
echo "🎵 Happy downloading!"