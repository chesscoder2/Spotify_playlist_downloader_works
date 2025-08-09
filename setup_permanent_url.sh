#!/bin/bash
# Setup Permanent URL Solutions for Spotify Downloader

echo "🌐 Setting up Permanent URL Solutions..."
echo "========================================"

# Function to install cloudflared
install_cloudflared() {
    echo "📥 Installing Cloudflare Tunnel (cloudflared)..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" ]]; then
        DOWNLOAD_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
    elif [[ "$ARCH" == "armv7l" ]]; then
        DOWNLOAD_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
    else
        echo "❌ Unsupported architecture: $ARCH"
        return 1
    fi
    
    wget -O cloudflared "$DOWNLOAD_URL"
    chmod +x cloudflared
    mv cloudflared $PREFIX/bin/
    echo "✅ Cloudflared installed successfully!"
}

# Function to install ngrok
install_ngrok() {
    echo "📥 Installing ngrok..."
    
    # Detect architecture  
    ARCH=$(uname -m)
    if [[ "$ARCH" == "aarch64" ]]; then
        DOWNLOAD_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
    elif [[ "$ARCH" == "armv7l" ]]; then
        DOWNLOAD_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz"
    else
        echo "❌ Unsupported architecture: $ARCH"
        return 1
    fi
    
    wget -O ngrok.tgz "$DOWNLOAD_URL"
    tar -xzf ngrok.tgz
    chmod +x ngrok
    mv ngrok $PREFIX/bin/
    rm ngrok.tgz
    echo "✅ ngrok installed successfully!"
}

# Install required packages
echo "📦 Installing required packages..."
pkg update
pkg install -y wget curl

# Menu for user choice
echo ""
echo "🔗 Choose your permanent URL solution:"
echo "1. Cloudflare Tunnel (Free, reliable, no signup needed)"
echo "2. ngrok (Free tier available, requires signup for custom domains)"
echo "3. Both (Recommended for flexibility)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        install_cloudflared
        ;;
    2)
        install_ngrok
        ;;
    3)
        install_cloudflared
        install_ngrok
        ;;
    *)
        echo "❌ Invalid choice. Installing Cloudflare Tunnel by default..."
        install_cloudflared
        ;;
esac

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Usage Instructions:"
echo ""

if command -v cloudflared &> /dev/null; then
    echo "🌐 Option 1: Cloudflare Tunnel (Free, Permanent)"
    echo "   ./start_cloudflare_tunnel.sh"
    echo "   - Gets a permanent subdomain like: https://abc-def-123.trycloudflare.com"
    echo "   - No registration required"
    echo "   - Stays active while running"
    echo ""
fi

if command -v ngrok &> /dev/null; then
    echo "🚀 Option 2: ngrok (More features with account)"
    echo "   ./start_ngrok_tunnel.sh"
    echo "   - Sign up at: https://ngrok.com/"
    echo "   - Free tier gives random URLs"
    echo "   - Paid tier allows custom domains"
    echo ""
fi

echo "💡 Pro Tip: Keep Termux running in background to maintain the tunnel!"