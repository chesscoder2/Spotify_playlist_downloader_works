#!/usr/bin/env python3
"""
Test script to verify Spotify access and find working playlists
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

def test_spotify_connection():
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Spotify credentials in .env file")
        return None
        
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test basic functionality
        results = sp.search(q='The Beatles', type='artist', limit=1)
        if results['artists']['items']:
            print("✅ Spotify API connection successful!")
            return sp
        else:
            print("❌ API connected but no search results")
            return None
            
    except Exception as e:
        print(f"❌ Spotify connection failed: {e}")
        return None

def find_public_playlists(sp):
    """Find some working public playlists"""
    print("\n🔍 Searching for accessible public playlists...")
    
    # Try different search terms
    search_terms = [
        "Today's Top Hits",
        "Pop Music",
        "Rock Classics", 
        "Hip Hop Central",
        "Chill Hits"
    ]
    
    working_playlists = []
    
    for term in search_terms:
        try:
            results = sp.search(q=f'"{term}"', type='playlist', limit=10)
            if results and 'playlists' in results and results['playlists']['items']:
                for playlist in results['playlists']['items']:
                    if playlist and 'id' in playlist:
                        playlist_id = playlist['id']
                        try:
                            # Test access
                            test_playlist = sp.playlist(playlist_id, fields="name,tracks.total,owner.display_name")
                            if test_playlist['tracks']['total'] > 0:
                                working_playlists.append({
                                    'name': test_playlist['name'],
                                    'id': playlist_id,
                                    'tracks': test_playlist['tracks']['total'],
                                    'owner': test_playlist.get('owner', {}).get('display_name', 'Unknown'),
                                    'url': f"https://open.spotify.com/playlist/{playlist_id}"
                                })
                                print(f"✅ {test_playlist['name']} ({test_playlist['tracks']['total']} tracks)")
                                
                                if len(working_playlists) >= 3:  # Found enough
                                    return working_playlists
                                    
                        except Exception as e:
                            continue  # Skip inaccessible playlists
                            
        except Exception as e:
            print(f"⚠️  Search failed for '{term}': {str(e)[:50]}...")
            continue
    
    return working_playlists

if __name__ == "__main__":
    print("🎵 Testing Spotify Access for Termux Downloader")
    print("=" * 50)
    
    sp = test_spotify_connection()
    if sp:
        working_playlists = find_public_playlists(sp)
        
        if working_playlists:
            print(f"\n✅ Found {len(working_playlists)} working playlists:")
            print("\nTry these URLs in your downloader:")
            for playlist in working_playlists:
                print(f"• {playlist['name']} - {playlist['tracks']} tracks")
                print(f"  {playlist['url']}")
                print()
        else:
            print("\n❌ No accessible public playlists found")
            print("This might be due to regional restrictions or API limitations")
    else:
        print("\n❌ Cannot test playlists without working Spotify connection")