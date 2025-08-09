#!/bin/bash
# Start Cloudflare Tunnel for permanent URL

echo "🌐 Starting Cloudflare Tunnel for Spotify Downloader..."
echo "======================================================"

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found! Please run:"
    echo "   ./setup_permanent_url.sh"
    exit 1
fi

# Check if web app is running
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "⚠️  Web app not running on localhost:5000"
    echo "Starting web app in background..."
    
    # Start web app in background
    nohup python web_app.py > web_app.log 2>&1 &
    WEB_PID=$!
    
    # Wait for web app to start
    echo "Waiting for web app to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5000 > /dev/null; then
            echo "✅ Web app started successfully!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Web app failed to start. Check web_app.log for errors."
            exit 1
        fi
    done
fi

echo ""
echo "🚀 Creating permanent tunnel..."
echo "This will generate a URL like: https://abc-def-123.trycloudflare.com"
echo ""
echo "🔗 Your permanent URL will be shown below:"
echo "📋 Copy and share this URL with anyone!"
echo ""
echo "🛑 Press Ctrl+C to stop the tunnel"
echo "💡 Keep this running to maintain the permanent link"
echo ""

# Start cloudflare tunnel
cloudflared tunnel --url http://localhost:5000