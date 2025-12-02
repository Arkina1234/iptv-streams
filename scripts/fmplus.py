import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Fetch data from API
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize lists for M3U and XML
m3u_lines = []
channels = []
programs = []

# M3U header
m3u_lines.append('#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/fmplus.xml"')

# Process each channel
for channel in data:
    # Extract channel info
    channel_id = channel.get('_id', '')
    name = channel.get('name', '')
    
    # Get thumbnails
    thumbnails = channel.get('thumbnails', {})
    thumbnail_url = thumbnails.get('light', '') if thumbnails else ''
    
    # Get site options
    site_options = channel.get('siteOptions', {})
    channel_number = site_options.get('channelNumber', '')
    
    # Get URL and encode brackets
    stream_url = channel.get('url', '')
    if stream_url:
        stream_url = stream_url.replace('[', '%5B').replace(']', '%5D')
    
    # Get EPG data
    epg = channel.get('epg', {})
    epg_entries = epg.get('entries', [])
    
    # Process first EPG entry if exists
    if epg_entries:
        epg_entry = epg_entries[0]
        epg_description = epg_entry.get('description', '')
        epg_start = epg_entry.get('start', '')
        epg_stop = epg_entry.get('stop', '')
        epg_title = epg_entry.get('title', '')
        
        # Format start and stop times
        try:
            start_time = datetime.strptime(epg_start, '%Y-%m-%dT%H:%M:%S.%fZ')
            stop_time = datetime.strptime(epg_stop, '%Y-%m-%dT%H:%M:%S.%fZ')
            start_formatted = start_time.strftime('%Y%m%d%H%M%S')
            stop_formatted = stop_time.strftime('%Y%m%d%H%M%S')
        except:
            start_formatted = ''
            stop_formatted = ''
        
        # Process title and description
        title = epg_title.replace('&', '&amp;') if epg_title else ''
        description = name if name else ''
        if epg_description:
            if description:
                description += ' - '
            description += epg_description.replace('&', '&amp;')
        
        # Add program to XML
        if channel_id and start_formatted and stop_formatted:
            programs.append({
                'channel_id': channel_id,
                'start': start_formatted,
                'stop': stop_formatted,
                'title': title,
                'description': description
            })
    
    # Add to M3U playlist
    m3u_lines.append(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-chno="{channel_number}" tvg-logo="{thumbnail_url}",{name}')
    m3u_lines.append(stream_url)
    
    # Add channel to XML
    if channel_id:
        channels.append({
            'id': channel_id,
            'name': name,
            'thumbnail': thumbnail_url
        })

# Generate M3U file
with open('m3u/fmplus.m3u', 'w', encoding='utf-8') as f:
    f.write('\n'.join(m3u_lines))

# Generate XMLTV file
tv = ET.Element('tv')
tv.set('source-info-url', 'https://bitcentral.com')
tv.set('source-info-name', 'Bitcentral, Inc.')
tv.set('generator-info-name', '')

# Add channels
for channel in channels:
    channel_elem = ET.SubElement(tv, 'channel')
    channel_elem.set('id', channel['id'])
    
    display_name = ET.SubElement(channel_elem, 'display-name')
    display_name.text = channel['name'].replace('&', '&amp;') if channel['name'] else ''
    
    if channel['thumbnail']:
        icon = ET.SubElement(channel_elem, 'icon')
        icon.set('src', channel['thumbnail'])

# Add programs
for program in programs:
    programme = ET.SubElement(tv, 'programme')
    programme.set('start', f"{program['start']} +0000")
    programme.set('stop', f"{program['stop']} +0000")
    programme.set('channel', program['channel_id'])
    
    title = ET.SubElement(programme, 'title')
    title.text = program['title']
    
    desc = ET.SubElement(programme, 'desc')
    desc.text = program['description']

# Format XML nicely
xml_str = ET.tostring(tv, encoding='utf-8')
parsed = minidom.parseString(xml_str)
pretty_xml = parsed.toprettyxml(indent='  ')

# Save XML file
with open('epg/fmplus.xml', 'w', encoding='utf-8') as f:
    f.write(pretty_xml)

print(f"Generated {len(channels)} channels")
print("Files created:")
print("- m3u/fmplus.m3u")
print("- epg/fmplus.xml")
