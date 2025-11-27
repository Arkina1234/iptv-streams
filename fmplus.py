import requests
import json
from datetime import datetime

# Make the API request
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize content
m3u_content = "#EXTM3U\n"
xmltv_content = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">\n'''

# Process all channels
for channel in data:
    # Extract channel information
    epg_description = channel['epg']['entries'][0]['description'] if channel['epg']['entries'][0].get('description') else None
    epg_start = channel['epg']['entries'][0]['start']
    epg_stop = channel['epg']['entries'][0]['stop']
    epg_title = channel['epg']['entries'][0]['title']
    thumbnails = channel['thumbnails']['light']
    channel_id = channel['_id']
    name = channel['name']
    stream_url = channel['url']

    # Process EPG data
    description = epg_description if epg_description else ""
    if description:
        description = description.replace('&', '&amp;')

    start = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
    stop = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")

    title = epg_title if epg_title else ""
    if title:
        title = title.replace('&', '&amp;')

    # Process stream URL
    stream = stream_url.replace('[', '%5B').replace(']', '%5D')

    # Add to M3U content
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_content += f'{stream}\n'

    # Add to XMLTV content
    xmltv_content += f'    <channel id="{channel_id}">\n'
    xmltv_content += f'        <display-name>{name}</display-name>\n'
    xmltv_content += f'        <icon src="{thumbnails}" />\n'
    xmltv_content += f'    </channel>\n'
    xmltv_content += f'    <programme start="{start} +0000" stop="{stop} +0000" channel="{channel_id}">\n'
    xmltv_content += f'        <title lang="en">{title}</title>\n'
    xmltv_content += f'        <desc lang="en">{description}</desc>\n'
    xmltv_content += f'    </programme>\n'

# Close XMLTV content
xmltv_content += '</tv>'

# Save to files
with open('fmplus.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

with open('fmplus.xml', 'w', encoding='utf-8') as f:
    f.write(xmltv_content)

print("Files saved successfully!")
print("M3U file: fmplus.m3u")
print("XMLTV file: fmplus.xml")