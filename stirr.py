import requests
import json

# Make the API request
url = "https://stirr.com/api/videos/list/?categories=all_categories&content_type=4&no_limit=true"
response = requests.get(url)
data = response.json()

# Extract videos
videos = data['videos']['category_videos'][0]

# Create M3U playlist
m3u_content = "#EXTM3U\n"

for video in videos:
    videoid = video.get('videoid')
    title = video.get('title')
    live = video.get('live')
    square_thumbs = video.get('square_thumbs', {}).get('original') if video.get('square_thumbs') else None
    
    # Add entry to M3U playlist
    m3u_content += f'#EXTINF:-1 tvg-id="{videoid}" tvg-logo="{square_thumbs}",{title}\n'
    m3u_content += f'{live}\n'

# Save to output file
with open('m3u/stirr.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

print("M3U playlist saved to stirr.m3u")