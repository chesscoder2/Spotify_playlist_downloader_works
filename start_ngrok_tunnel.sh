#!/bin/bash
# Start ngrok tunnel for permanent URL

echo "🚀 Starting ngrok Tunnel for Spotify Downloader..."
echo "================================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found! Please run:"
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

# Check if ngrok is authenticated
if ! ngrok config check > /dev/null 2>&1; then
    echo "⚠️  ngrok not authenticated!"
    echo "📋 Steps to authenticate:"
    echo "1. Sign up at: https://ngrok.com/"
    echo "2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE"
    echo ""
    read -p "Enter your ngrok authtoken (or press Enter to use free tier): " authtoken
    
    if [ ! -z "$authtoken" ]; then
        ngrok config add-authtoken "$authtoken"
        echo "✅ ngrok authenticated!"
    else
        echo "🆓 Using ngrok free tier (limited sessions)"
    fi
fi

echo ""
echo "🚀 Creating ngrok tunnel..."
echo "This will generate a URL like: https://abc123.ngrok.io"
echo ""
echo "🔗 Your permanent URL will be shown below:"
echo "📋 Copy and share this URL with anyone!"
echo ""
echo "🛑 Press Ctrl+C to stop the tunnel"
echo "💡 Keep this running to maintain the permanent link"
echo ""

# Start ngrok tunnel
ngrok http 5000