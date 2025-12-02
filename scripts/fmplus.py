import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Any

def fetch_data():
    """Fetch data from the API endpoint"""
    url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def sanitize_text(text: str) -> str:
    """Replace special characters for XML compatibility"""
    if not text:
        return ""
    # Replace & with &amp; and handle other XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def generate_m3u(channels: List[Dict[str, Any]]) -> str:
    """Generate M3U playlist content"""
    m3u_content = '#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/fmplus.xml"\n'
    
    for channel in channels:
        id = channel.get('_id', '')
        name = channel.get('name', '')
        thumbnails = channel.get('thumbnails', {}).get('light', '')
        channel_number = channel.get('siteOptions', {}).get('channelNumber', '')
        stream_url = channel.get('url', '')
        
        # Encode stream URL
        stream_url = stream_url.replace('[', '%5B').replace(']', '%5D')
        
        # Add channel info
        m3u_content += f'#EXTINF:-1 tvg-id="{id}" tvg-chno="{channel_number}" tvg-logo="{thumbnails}",{name}\n'
        m3u_content += f'{stream_url}\n'
    
    return m3u_content

def generate_xml(channels: List[Dict[str, Any]]) -> str:
    """Generate XMLTV content"""
    xml_content = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv source-info-url="https://bitcentral.com" source-info-name="Bitcentral, Inc." generator-info-name="">\n'''
    
    # First, add all channels
    for channel in channels:
        id = channel.get('_id', '')
        name = sanitize_text(channel.get('name', ''))
        thumbnails = channel.get('thumbnails', {}).get('light', '')
        
        xml_content += f'''    <channel id="{id}">
        <display-name>{name}</display-name>
        <icon src="{thumbnails}" />
    </channel>\n'''
    
    # Then, add programmes
    for channel in channels:
        id = channel.get('_id', '')
        epg = channel.get('epg', {})
        entries = epg.get('entries', [])
        
        for entry in entries:
            description = sanitize_text(entry.get('description', ''))
            epg_start = entry.get('start', '')
            epg_stop = entry.get('stop', '')
            title = sanitize_text(entry.get('title', ''))
            
            if not epg_start or not epg_stop:
                continue
                
            try:
                # Parse and format timestamps
                start_dt = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ")
                stop_dt = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ")
                
                start_str = start_dt.strftime("%Y%m%d%H%M%S")
                stop_str = stop_dt.strftime("%Y%m%d%H%M%S")
                
                xml_content += f'''    <programme start="{start_str} +0000" stop="{stop_str} +0000" channel="{id}">
        <title>{title}</title>
        <desc>{description}</desc>
    </programme>\n'''
            except (ValueError, KeyError) as e:
                print(f"Error parsing date for channel {id}: {e}")
                continue
    
    xml_content += '</tv>'
    return xml_content

def save_to_file(filename: str, content: str):
    """Save content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving to file {filename}: {e}")

def main():
    # Fetch data from API
    data = fetch_data()
    if not data:
        print("Failed to fetch data. Exiting...")
        return
    
    # Generate M3U playlist
    m3u_content = generate_m3u(data)
    save_to_file('m3u/fmplus.m3u', m3u_content)
    
    # Generate XMLTV guide
    xml_content = generate_xml(data)
    save_to_file('epg/fmplus.xml', xml_content)
    
    print(f"Processed {len(data)} channels")

if __name__ == "__main__":
    main()
