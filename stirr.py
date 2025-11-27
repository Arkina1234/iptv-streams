import requests
import json

try:
    # Make the API request
    url = "https://stirr.com/api/videos/list/?categories=all_categories&content_type=4&no_limit=true"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    data = response.json()

    # Extract video data safely
    videos = data.get('videos', {}).get('category_videos', [])
    
    if not videos or not videos[0]:
        print("No videos found")
        exit()

    # Create M3U playlist
    m3u_content = "#EXTM3U\n"

    for video in videos[0]:
        videoid = video.get('videoid', '')
        title = video.get('title', 'Unknown Title')
        live = video.get('live', '')
        square_thumbs = video.get('square_thumbs', {}).get('original', '') if video.get('square_thumbs') else ''
        
        # Add entry to M3U playlist
        m3u_content += f'#EXTINF:-1 tvg-id="{videoid}" tvg-logo="{square_thumbs}",{title}\n'
        m3u_content += f'{live}\n'

    # Save to output file
    with open('stirr.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    print(f"M3U playlist saved to stirr.m3u with {len(videos[0])} entries")

except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")