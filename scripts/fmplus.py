import json
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Fetch the JSON data
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize lists for M3U and XML content
m3u_lines = []
channels_data = []

# Parse each channel
for channel in data:
    # Extract channel information with safe access
    epg = channel.get('epg', {})
    entries = epg.get('entries', [{}]) if epg else [{}]
    
    epg_description = entries[0].get('description') if entries else None
    epg_start = entries[0].get('start') if entries else None
    epg_stop = entries[0].get('stop') if entries else None
    epg_title = entries[0].get('title') if entries else None
    
    thumbnails = channel.get('thumbnails', {}).get('light')
    channel_id = channel.get('_id')
    name = channel.get('name')
    channel_number = channel.get('siteOptions', {}).get('channelNumber')
    stream_url = channel.get('url')
    
    # Clean up description and title
    description = str(epg_description).replace('&', '&amp;') if epg_description else ''
    title = str(epg_title).replace('&', '&amp;') if epg_title else ''
    
    # Format dates
    start_timestamp = ''
    stop_timestamp = ''
    if epg_start:
        try:
            dt = datetime.fromisoformat(epg_start.replace('Z', '+00:00'))
            start_timestamp = dt.strftime('%Y%m%d%H%M%S')
        except:
            start_timestamp = ''
    
    if epg_stop:
        try:
            dt = datetime.fromisoformat(epg_stop.replace('Z', '+00:00'))
            stop_timestamp = dt.strftime('%Y%m%d%H%M%S')
        except:
            stop_timestamp = ''
    
    # Encode stream URL
    stream = stream_url.replace('[', '%5B').replace(']', '%5D') if stream_url else ''
    
    # Prepare channel data for XML
    channels_data.append({
        'id': channel_id,
        'name': name.replace('&', '&amp;') if name else '',
        'thumbnails': thumbnails,
        'start': start_timestamp,
        'stop': stop_timestamp,
        'title': title,
        'description': description,
        'channel_number': channel_number
    })
    
    # Add to M3U playlist
    if channel_id and name and stream:
        m3u_lines.append(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-chno="{channel_number or ""}" tvg-logo="{thumbnails or ""}",{name}')
        m3u_lines.append(stream)

# Create M3U file
m3u_content = '#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/fmplus.xml"\n'
m3u_content += '\n'.join(m3u_lines)

# Create XML file
tv = ET.Element('tv', {
    'source-info-url': 'https://epg.unreel.me',
    'source-info-name': 'Bitcentral',
    'generator-info-name': ''
})

# Add channels and programs
for channel_data in channels_data:
    if not channel_data['id']:
        continue
    
    # Add channel
    channel = ET.SubElement(tv, 'channel', {'id': channel_data['id']})
    display_name = ET.SubElement(channel, 'display-name')
    display_name.text = channel_data['name']
    
    if channel_data['thumbnails']:
        icon = ET.SubElement(channel, 'icon', {'src': channel_data['thumbnails']})
    
    # Add program if we have EPG data
    if channel_data['start'] and channel_data['stop']:
        programme = ET.SubElement(tv, 'programme', {
            'start': f"{channel_data['start']} +0000",
            'stop': f"{channel_data['stop']} +0000",
            'channel': channel_data['id']
        })
        
        title_elem = ET.SubElement(programme, 'title')
        title_elem.text = channel_data['title']
        
        if channel_data['description']:
            desc_elem = ET.SubElement(programme, 'desc')
            desc_elem.text = channel_data['description']

# Pretty print XML
xml_str = ET.tostring(tv, encoding='utf-8').decode()
xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")

# Remove the XML declaration from minidom and add our custom one
xml_pretty = xml_pretty.split('\n', 1)[1]  # Remove first line (minidom's declaration)
xml_final = '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + xml_pretty

# Save to files
with open('m3u/fmplus.m3u', 'w', encoding='utf-8') as f:
    f.write(m3u_content)

with open('epg/fmplus.xml', 'w', encoding='utf-8') as f:
    f.write(xml_final)

print("Files created successfully:")
print("- m3u/fmplus.m3u")
print("- epg/fmplus.xml")
