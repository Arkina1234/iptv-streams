import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.parse

# Make the API request
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Process each channel
m3u_content = "#EXTM3U\n"
xml_channels = []
xml_programmes = []

for channel in data:
    # Extract channel data
    epg_description = channel.get('epg', {}).get('entries', [{}])[0].get('description') if channel.get('epg', {}).get('entries') else None
    epg_start = channel.get('epg', {}).get('entries', [{}])[0].get('start') if channel.get('epg', {}).get('entries') else None
    epg_stop = channel.get('epg', {}).get('entries', [{}])[0].get('stop') if channel.get('epg', {}).get('entries') else None
    epg_title = channel.get('epg', {}).get('entries', [{}])[0].get('title') if channel.get('epg', {}).get('entries') else None
    thumbnails = channel.get('thumbnails', {}).get('light', '')
    channel_id = channel.get('_id', '')
    name = channel.get('name', '')
    stream_url = channel.get('url', '')
    
    # Process stream URL
    stream = stream_url.replace('[', '%5B').replace(']', '%5D')
    
    # Add to M3U content
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_content += f'{stream}\n'
    
    # Prepare XML data
    xml_channels.append({
        'id': channel_id,
        'name': name,
        'thumbnails': thumbnails
    })
    
    # Add programme data if available
    if epg_start and epg_stop and epg_title:
        # Convert timestamps
        start_dt = datetime.fromisoformat(epg_start.replace('Z', '+00:00'))
        stop_dt = datetime.fromisoformat(epg_stop.replace('Z', '+00:00'))
        
        start_formatted = start_dt.strftime("%Y%m%d%H%M%S")
        stop_formatted = stop_dt.strftime("%Y%m%d%H%M%S")
        
        # Escape XML special characters
        title_escaped = epg_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        description_escaped = epg_description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;') if epg_description else ''
        
        xml_programmes.append({
            'start': start_formatted,
            'stop': stop_formatted,
            'channel': channel_id,
            'title': title_escaped,
            'description': description_escaped
        })

# Generate XML content
xml_content = '<?xml version="1.0" encoding="UTF-8" ?>\n'
xml_content += '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
xml_content += '<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">\n'

# Add channels
for channel in xml_channels:
    xml_content += f'    <channel id="{channel["id"]}">\n'
    xml_content += f'        <display-name>{channel["name"]}</display-name>\n'
    if channel['thumbnails']:
        xml_content += f'        <icon src="{channel["thumbnails"]}" />\n'
    xml_content += '    </channel>\n'

# Add programmes
for programme in xml_programmes:
    xml_content += f'    <programme start="{programme["start"]} +0000" stop="{programme["stop"]} +0000" channel="{programme["channel"]}">\n'
    xml_content += f'        <title lang="en">{programme["title"]}</title>\n'
    if programme['description']:
        xml_content += f'        <desc lang="en">{programme["description"]}</desc>\n'
    xml_content += '    </programme>\n'

xml_content += '</tv>'

# Save to files
with open('fmplus.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

with open('fmplus.xml', 'w', encoding='utf-8') as f:
    f.write(xml_content)

print("Files generated successfully!")
print(f"M3U playlist saved as: fmplus.m3u")
print(f"XML EPG saved as: fmplus.xml")