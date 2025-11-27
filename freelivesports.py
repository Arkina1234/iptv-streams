import requests
import json
from datetime import datetime

# Make the API request
url = "https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize content
m3u_content = "#EXTM3U\n"
xmltv_content = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">'''

# Process all channels
for channel in data:
    # Extract channel information
    channel_id = channel['_id']
    name = channel['name']
    stream_url = channel['url']
    thumbnails = channel['thumbnails']['light']

    # Add to M3U
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n{stream_url}\n'

    # Add channel to XMLTV
    xmltv_content += f'''
<channel id="{channel_id}">
<display-name>{name}</display-name>
<icon src="{thumbnails}" />
</channel>'''

    # Add EPG entries if available
    if 'epg' in channel and channel['epg']['entries']:
        for entry in channel['epg']['entries']:
            epg_description = entry.get('description', '')
            epg_start = entry['start']
            epg_stop = entry['stop']
            epg_title = entry['title']

            # Convert timestamps
            start_timestamp = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
            stop_timestamp = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")

            xmltv_content += f'''
<programme start="{start_timestamp} +0000" stop="{stop_timestamp} +0000" channel="{channel_id}">
<title lang="en">{epg_title}</title>
<desc lang="en">{epg_description}</desc>
</programme>'''

# Close XMLTV
xmltv_content += "\n</tv>"

# Save to files
with open('freelivesports.m3u', 'w', encoding='utf-8') as m3u_file:
    m3u_file.write(m3u_content)

with open('freelivesports.xml', 'w', encoding='utf-8') as xml_file:
    xml_file.write(xmltv_content)

print("Files saved successfully!")
print("M3U file: freelivesports.m3u")
print("XMLTV file: freelivesports.xml")