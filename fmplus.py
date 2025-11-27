import requests
import json
from datetime import datetime

# Make the API request
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Generate M3U output for all channels
m3u_output = "#EXTM3U\n"
for channel in data:
    channel_id = channel['_id']
    name = channel['name']
    thumbnails = channel['thumbnails']['light']
    stream_url = channel['url'].replace('[', '%5B').replace(']', '%5D')
    
    m3u_output += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_output += f'{stream_url}\n'

# Generate XML output for all channels
xml_output = '<?xml version="1.0" encoding="UTF-8" ?>\n'
xml_output += '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
xml_output += '<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">\n'

# Add channels
for channel in data:
    channel_id = channel['_id']
    name = channel['name'].replace('&', '&amp;')
    thumbnails = channel['thumbnails']['light']
    
    xml_output += f'    <channel id="{channel_id}">\n'
    xml_output += f'        <display-name>{name}</display-name>\n'
    xml_output += f'        <icon src="{thumbnails}" />\n'
    xml_output += '    </channel>\n'

# Add programmes
for channel in data:
    channel_id = channel['_id']
    
    if channel['epg']['entries']:
        for entry in channel['epg']['entries']:
            epg_description = entry.get('description', '')
            epg_start = entry['start']
            epg_stop = entry['stop']
            epg_title = entry['title']
            
            description = epg_description.replace('&', '&amp;') if epg_description else ""
            start = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
            stop = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
            title = epg_title.replace('&', '&amp;') if epg_title else ""
            
            xml_output += f'    <programme start="{start} +0000" stop="{stop} +0000" channel="{channel_id}">\n'
            xml_output += f'        <title lang="en">{title}</title>\n'
            xml_output += f'        <desc lang="en">{description}</desc>\n'
            xml_output += '    </programme>\n'

xml_output += '</tv>'

# Save to files
with open('fmplus.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_output)

with open('fmplus.xml', 'w', encoding='utf-8') as f:
    f.write(xml_output)

print("Files saved: fmplus.m3u and fmplus.xml")