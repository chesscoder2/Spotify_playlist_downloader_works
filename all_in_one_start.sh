#!/bin/bash
# All-in-One Startup Script for Spotify Downloader with Permanent URL

echo "🎵 Spotify YouTube Downloader - All-in-One Startup"
echo "=================================================="

# Function to check if web app is ready
check_web_app() {
    for i in {1..30}; do
        if curl -s http://localhost:5000 > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy and edit .env.example:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

echo "🌐 Starting web application..."

# Start web app in background
python web_app.py &
WEB_PID=$!

# Wait for web app to be ready
echo "⏳ Waiting for web application to start..."
if check_web_app; then
    echo "✅ Web application is running!"
else
    echo "❌ Failed to start web application"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

# Show local access info
LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[^ ]+' | head -1)
echo ""
echo "📱 Local Access URLs:"
echo "   http://localhost:5000"
if [ "$LOCAL_IP" != "" ]; then
    echo "   http://$LOCAL_IP:5000 (share with WiFi users)"
fi

echo ""
echo "🌐 Choose Permanent URL Option:"
echo "1. Cloudflare Tunnel (Free, no signup)"
echo "2. ngrok (Free tier, better with account)"  
echo "3. Local only (no permanent URL)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        if command -v cloudflared &> /dev/null; then
            echo ""
            echo "🚀 Starting Cloudflare Tunnel..."
            echo "🔗 Your permanent URL:"
            cloudflared tunnel --url http://localhost:5000
        else
            echo "❌ cloudflared not installed. Run: ./setup_permanent_url.sh"
        fi
        ;;
    2)
        if command -v ngrok &> /dev/null; then
            echo ""
            echo "🚀 Starting ngrok Tunnel..."
            echo "🔗 Your permanent URL:"
            ngrok http 5000
        else
            echo "❌ ngrok not installed. Run: ./setup_permanent_url.sh"
        fi
        ;;
    3)
        echo ""
        echo "✅ Running locally only"
        echo "🛑 Press Ctrl+C to stop"
        wait $WEB_PID
        ;;
    *)
        echo "❌ Invalid choice. Running locally only."
        wait $WEB_PID
        ;;
esac

# Cleanup
kill $WEB_PID 2>/dev/null