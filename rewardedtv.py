import requests
import json

# Make the API request
url = "https://epg.unreel.me/v2/sites/rewardedtv/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Generate M3U content
m3u_content = "#EXTM3U\n"

for item in data:
    thumbnails = item['thumbnails']['light']
    channel_id = item['_id']
    name = item['name']
    url = item['url']
    
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_content += f'{url}\n'

# Save to output file
with open('rewardedtv.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

print("M3U file saved as 'rewardedtv.m3u'")


except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")