# Overview

This project is a Spotify playlist to YouTube downloader specifically optimized for mobile Android devices running Termux. The application downloads **maximum quality audio** with intelligent format selection (FLAC > Opus/WebM > AAC/M4A > 320kbps MP3) from YouTube based on Spotify playlist tracks, with complete metadata embedding and high-resolution album artwork. It's designed to handle mobile device constraints like limited memory, battery optimization, and Android-specific storage permissions.

## Recent Changes (August 2025)

### Major Architecture Improvements:
- **New main.py**: Complete rewrite with enhanced audio quality prioritization and mobile optimization
- **Maximum Quality Engine**: Intelligent format selection prioritizing lossless FLAC, then high-bitrate Opus/WebM, AAC/M4A, and MP3 
- **Enhanced Termux Integration**: Automatic environment detection, storage permission handling, and Android-specific optimizations
- **Improved Metadata System**: Using mutagen library for comprehensive metadata embedding (replaced eyed3)
- **Mobile-First Design**: Battery awareness, memory monitoring, and network condition handling
- **Progress Visualization**: Added tqdm progress bars and colorama terminal colors for better UX

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The system follows a modular Python architecture with a main downloader class and specialized utility modules:

- **Main Controller**: `TermuxSpotifyDownloader` class handles the primary workflow orchestration
- **Utility Modules**: Separated concerns into specialized helpers for Termux integration, audio quality management, and mobile optimizations
- **Configuration-driven**: Uses environment variables for API credentials and settings

## Audio Processing Pipeline
The application implements a sophisticated audio quality management system:

- **Quality Prioritization**: FLAC > Opus/WebM > High-quality M4A > 320kbps MP3 > Best available
- **Metadata Embedding**: Complete ID3 tag support with album artwork, track info, and album details
- **Format Flexibility**: Supports multiple audio formats (MP3, FLAC, M4A, OGG) with automatic conversion

## Mobile-Specific Optimizations
Designed specifically for resource-constrained mobile environments:

- **Memory Management**: Monitors available memory and implements low-memory modes
- **Battery Awareness**: Checks battery status and adjusts behavior accordingly
- **Image Optimization**: Resizes album artwork to mobile-appropriate dimensions (max 800x800)
- **Progress Tracking**: Mobile-friendly progress indicators with ETA calculations

## Termux Integration Layer
Specialized Android/Termux environment handling:

- **Environment Detection**: Automatically detects Termux runtime environment
- **Permission Management**: Handles Android storage permissions through termux-setup-storage
- **API Integration**: Leverages Termux:API for notifications and system integration
- **Storage Optimization**: Manages temporary files and download locations appropriately

## Error Handling and Resilience
Built for mobile network conditions and interruptions:

- **Resume Capability**: Handles interrupted downloads and retries failed attempts
- **Network Awareness**: Adapts to mobile network conditions
- **Graceful Degradation**: Falls back to lower quality when high-quality sources unavailable

# External Dependencies

## API Services
- **Spotify Web API**: Uses spotipy library with client credentials flow for playlist access
- **YouTube**: Leverages yt-dlp for video/audio extraction and download
- **Termux:API**: Optional but recommended for Android system integration and notifications

## Core Libraries
- **spotipy**: Spotify API wrapper for playlist and track metadata retrieval
- **yt-dlp**: Advanced YouTube downloader with format selection and quality options
- **mutagen**: Audio metadata manipulation (ID3 tags, FLAC metadata)
- **PIL/Pillow**: Image processing for album artwork optimization
- **psutil**: System resource monitoring for memory and CPU usage
- **requests**: HTTP client for artwork downloading and API calls

## System Integration
- **FFmpeg**: Audio format conversion and processing (bundled with yt-dlp)
- **Android Storage Framework**: Access to external storage through Termux permissions
- **Termux Environment**: Specialized mobile Linux environment with Android integration