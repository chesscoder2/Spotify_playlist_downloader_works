#!/bin/bash
# Startup script for Spotify Downloader Web Interface

echo "🎵 Starting Spotify YouTube Downloader Web Interface..."
echo "======================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy and edit .env.example:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Get local IP address for sharing
if command -v ip &> /dev/null; then
    LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[^ ]+' | head -1)
elif command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
else
    LOCAL_IP="localhost"
fi

echo "🌐 Starting web server..."
echo "📱 Local access: http://localhost:5000"
if [ "$LOCAL_IP" != "localhost" ]; then
    echo "🔗 Network access: http://$LOCAL_IP:5000"
    echo "📡 Share this URL with others on the same WiFi network"
fi
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the web application
python web_app.py