import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Fetch data from the API
url = "https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize lists for storing output
m3u_lines = []
channels = []
programmes = []

# Create XML root
tv = ET.Element('tv')
tv.set('source-info-url', 'https://bitcentral.com')
tv.set('source-info-name', 'Bitcentral, Inc.')
tv.set('generator-info-name', '')

# Process each channel
for channel_data in data:
    # Extract data with fallbacks
    epg_entries = channel_data.get('epg', {}).get('entries', [{}])
    epg_entry = epg_entries[0] if epg_entries else {}
    
    epg_description = epg_entry.get('description')
    epg_start = epg_entry.get('start')
    epg_stop = epg_entry.get('stop')
    epg_title = epg_entry.get('title')
    
    thumbnails = channel_data.get('thumbnails', {}).get('light')
    channel_id = channel_data.get('_id')
    name = channel_data.get('name')
    channel_number = channel_data.get('siteOptions', {}).get('channelNumber')
    stream_url = channel_data.get('url')
    
    # Process data
    description = name
    if epg_description:
        description = epg_description.replace('&', '&amp;')
    
    start_time = ''
    stop_time = ''
    if epg_start:
        start_time = datetime.fromisoformat(epg_start.replace('Z', '+00:00')).strftime('%Y%m%d%H%M%S')
    if epg_stop:
        stop_time = datetime.fromisoformat(epg_stop.replace('Z', '+00:00')).strftime('%Y%m%d%H%M%S')
    
    title = ''
    if epg_title:
        title = epg_title.replace('&', '&amp;')
    
    # Process stream URL
    stream = stream_url.replace('[', '%5B').replace(']', '%5D') if stream_url else ''
    
    # Add to M3U playlist
    m3u_lines.append(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-chno="{channel_number}" tvg-logo="{thumbnails}",{name}')
    m3u_lines.append(stream)
    
    # Create XML channel element
    channel = ET.SubElement(tv, 'channel')
    channel.set('id', channel_id)
    
    display_name = ET.SubElement(channel, 'display-name')
    display_name.text = name.replace('&', '&amp;') if name else ''
    
    if thumbnails:
        icon = ET.SubElement(channel, 'icon')
        icon.set('src', thumbnails)
    
    # Create XML programme element if we have EPG data
    if start_time and stop_time and title:
        programme = ET.SubElement(tv, 'programme')
        programme.set('start', f'{start_time} +0000')
        programme.set('stop', f'{stop_time} +0000')
        programme.set('channel', channel_id)
        
        title_elem = ET.SubElement(programme, 'title')
        title_elem.text = title
        
        desc_elem = ET.SubElement(programme, 'desc')
        desc_elem.text = description if description else ''
    
    # Store for debugging/other uses
    channels.append({
        'id': channel_id,
        'name': name,
        'number': channel_number,
        'logo': thumbnails,
        'stream': stream
    })
    
    if start_time and stop_time and title:
        programmes.append({
            'channel_id': channel_id,
            'start': start_time,
            'stop': stop_time,
            'title': title,
            'description': description
        })

# Add M3U header
m3u_header = ['#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/freelivesports.xml"']
m3u_content = m3u_header + m3u_lines

# Save M3U file
with open('m3u/freelivesports.m3u', 'w', encoding='utf-8') as f:
    f.write('\n'.join(m3u_content))

# Save XML file with proper formatting
xml_str = ET.tostring(tv, encoding='unicode', method='xml')

# Pretty print the XML
xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")

# Remove the XML declaration from minidom and add our custom one
xml_pretty = xml_pretty.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">')

with open('epg/freelivesports.xml', 'w', encoding='utf-8') as f:
    f.write(xml_pretty)

print(f"Processed {len(channels)} channels")
print(f"Generated {len(programmes)} programme entries")
print("Files saved: m3u/freelivesports.m3u and epg/freelivesports.xml")
