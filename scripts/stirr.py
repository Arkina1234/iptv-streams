import requests
import json

def get_video_list():
    """Get all videos from STIRR API"""
    url = "https://stirr.com/api/videos/list/?categories=all_categories&content_type=4&no_limit=true"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

def get_playable_url(videoid):
    """Get playable URL for a specific video ID"""
    url = f"https://stirr.com/api/v2/videos/{videoid}/playable"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    data = response.json()
    
    if (data.get('data') and 
        len(data['data']) > 0 and 
        data['data'][0].get('media') and 
        len(data['data'][0]['media']) > 0):
        return data['data'][0]['media'][0]
    return None

def generate_m3u_playlist():
    """Generate M3U playlist from STIRR data"""
    data = get_video_list()
    channels = []
    
    # Extract all videos
    for category in data.get('videos', {}).get('category_videos', []):
        for video in category:
            videoid = video.get('videoid')
            if not videoid:
                continue
                
            title = video.get('title', '').replace(',', '')
            sequence = video.get('sequence', '')
            
            # Get thumbnail
            square_thumbs = ''
            if video.get('square_thumbs') and '512x512' in video['square_thumbs']:
                square_thumbs = video['square_thumbs']['512x512']
            
            # Get playable URL
            live_url = get_playable_url(videoid)
            
            if live_url:
                channels.append({
                    'videoid': videoid,
                    'title': title,
                    'sequence': sequence,
                    'logo': square_thumbs,
                    'url': live_url
                })
    
    # Generate M3U content
    m3u_content = '#EXTM3U url-tvg="https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/Stirr/all.xml"\n\n'
    
    for channel in channels:
        m3u_content += f'#EXTINF:-1 tvg-id="{channel["videoid"]}" tvg-chno="{channel["sequence"]}" tvg-logo="{channel["logo"]}",{channel["title"]}\n'
        m3u_content += f'{channel["url"]}\n'
    
    return m3u_content, len(channels)

def save_playlist(filename='m3u/stirr.m3u'):
    """Save the generated playlist to a file"""
    m3u_content, channel_count = generate_m3u_playlist()
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"Playlist saved to {filename} with {channel_count} channels")
    return filename

# Run the script
if __name__ == "__main__":
    save_playlist()
