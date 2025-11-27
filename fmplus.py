import requests
import json
from datetime import datetime

# Make the API request
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize output strings
m3u_output = "#EXTM3U\n"
xmltv_output = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">
'''

# Process each channel in the response
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

    # Process text fields
    description = str(epg_description).replace('&', '&amp;') if epg_description else ""
    start = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
    stop = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
    title = str(epg_title).replace('&', '&amp;')

    # Process stream URL
    stream = stream_url.replace('[', '%5B').replace(']', '%5D')

    # Add to M3U output
    m3u_output += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_output += f'{stream}\n'

    # Add to XMLTV output
    xmltv_output += f'    <channel id="{channel_id}">\n'
    xmltv_output += f'        <display-name>{name}</display-name>\n'
    xmltv_output += f'        <icon src="{thumbnails}" />\n'
    xmltv_output += f'    </channel>\n'
    xmltv_output += f'    <programme start="{start} +0000" stop="{stop} +0000" channel="{channel_id}">\n'
    xmltv_output += f'        <title lang="en">{title}</title>\n'
    xmltv_output += f'        <desc lang="en">{description}</desc>\n'
    xmltv_output += f'    </programme>\n'

# Close XMLTV tag
xmltv_output += '</tv>'

# Save to files
with open("fmplus.m3u", "w", encoding="utf-8") as m3u_file:
    m3u_file.write(m3u_output)

with open("fmplus.xml", "w", encoding="utf-8") as xml_file:
    xml_file.write(xmltv_output)

print("Files created successfully!")
print("M3U file: fmplus.m3u")
print("XMLTV file: fmplus.xml")