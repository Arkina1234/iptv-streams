import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

def fetch_data():
    """Fetch data from the API"""
    url = "https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/081f73704b56aaceb6b459804761ec54"
    response = requests.get(url)
    return response.json()

def process_channel(channel_data):
    """Process a single channel's data"""
    # Extract data
    epg_entries = channel_data.get('epg', {}).get('entries', [{}])
    epg_entry = epg_entries[0] if epg_entries else {}
    
    # Get values with fallbacks
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
    
    # Parse dates
    start_time = ''
    stop_time = ''
    if epg_start:
        dt = datetime.fromisoformat(epg_start.replace('Z', '+00:00'))
        start_time = dt.strftime('%Y%m%d%H%M%S')
    if epg_stop:
        dt = datetime.fromisoformat(epg_stop.replace('Z', '+00:00'))
        stop_time = dt.strftime('%Y%m%d%H%M%S')
    
    title = ''
    if epg_title:
        title = epg_title.replace('&', '&amp;')
    
    # Process stream URL
    stream = stream_url
    if stream_url:
        stream = stream_url.replace('[', '%5B').replace(']', '%5D')
    
    return {
        'id': channel_id,
        'name': name,
        'channel_number': channel_number,
        'logo': thumbnails,
        'stream': stream,
        'epg': {
            'start': start_time,
            'stop': stop_time,
            'title': title,
            'description': description
        }
    }

def create_m3u_playlist(channels):
    """Create M3U playlist content"""
    lines = ['#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/freelivesports.xml"']
    
    for channel in channels:
        lines.append(f'#EXTINF:-1 tvg-id="{channel["id"]}" tvg-chno="{channel["channel_number"]}" tvg-logo="{channel["logo"]}",{channel["name"]}')
        lines.append(channel['stream'])
    
    return '\n'.join(lines)

def create_xml_epg(channels):
    """Create XML EPG content"""
    tv = ET.Element('tv')
    tv.set('source-info-url', 'https://bitcentral.com')
    tv.set('source-info-name', 'Bitcentral, Inc.')
    tv.set('generator-info-name', '')
    
    for channel in channels:
        # Add channel element
        channel_elem = ET.SubElement(tv, 'channel')
        channel_elem.set('id', channel['id'])
        
        display_name = ET.SubElement(channel_elem, 'display-name')
        display_name.text = channel['name'].replace('&', '&amp;') if channel['name'] else ''
        
        if channel['logo']:
            icon = ET.SubElement(channel_elem, 'icon')
            icon.set('src', channel['logo'])
        
        # Add programme if EPG data exists
        if channel['epg']['start'] and channel['epg']['stop'] and channel['epg']['title']:
            programme = ET.SubElement(tv, 'programme')
            programme.set('start', f"{channel['epg']['start']} +0000")
            programme.set('stop', f"{channel['epg']['stop']} +0000")
            programme.set('channel', channel['id'])
            
            title_elem = ET.SubElement(programme, 'title')
            title_elem.text = channel['epg']['title']
            
            desc_elem = ET.SubElement(programme, 'desc')
            desc_elem.text = channel['epg']['description'] if channel['epg']['description'] else ''
    
    # Convert to pretty XML
    xml_str = ET.tostring(tv, encoding='unicode')
    xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # Add DOCTYPE declaration
    xml_pretty = xml_pretty.replace(
        '<?xml version="1.0" ?>',
        '<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">'
    )
    
    return xml_pretty

def main():
    """Main function"""
    # Fetch and process data
    data = fetch_data()
    channels = [process_channel(channel) for channel in data]
    
    # Create M3U playlist
    m3u_content = create_m3u_playlist(channels)
    with open('m3u/freelivesports.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    # Create XML EPG
    xml_content = create_xml_epg(channels)
    with open('epg/freelivesports.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    # Print summary
    programmes_count = sum(1 for c in channels if c['epg']['start'] and c['epg']['stop'] and c['epg']['title'])
    print(f"✓ Processed {len(channels)} channels")
    print(f"✓ Generated {programmes_count} programme entries")
    print("✓ Files saved:")
    print("  - m3u/freelivesports.m3u")
    print("  - epg/freelivesports.xml")

if __name__ == "__main__":
    main()
