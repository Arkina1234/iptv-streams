import requests
import json

# Make the API request
url = "https://stirr.com/api/videos/list/?categories=all_categories&content_type=4&no_limit=true"
response = requests.get(url)
data = response.json()

# Create M3U playlist
m3u_content = "#EXTM3U url-tvg=\"https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/Stirr/all.xml\"\n"

# Iterate through all videos
for category in data['videos']['category_videos']:
    for video in category:
        videoid = video.get('videoid')
        title = video.get('title', '')
        live = video.get('live', '')
        logo = video.get('logo')
        
        # Add entry to M3U playlist
        m3u_content += f'#EXTINF:-1 tvg-id="{videoid}" tvg-logo="{logo}",{title}\n'
        m3u_content += f'{live}\n'

# Save to output file
with open('m3u/stirr.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

print("M3U playlist saved to m3u/stirr.m3u")
