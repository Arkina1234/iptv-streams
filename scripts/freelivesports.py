import requests
import json
from datetime import datetime

# Fetch data
url = "https://epg.unreel.me/v2/sites/freelivesports/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Generate M3U
m3u = ['#EXTM3U url-tvg="https://arkina1234.github.io/iptv-streams/epg/freelivesports.xml"']

for channel in data:
    if not channel: continue
    
    # Channel info
    cid = channel.get('_id', '')
    name = channel.get('name', '')
    stream = channel.get('url', '').replace('[', '%5B').replace(']', '%5D')
    logo = channel.get('thumbnails', {}).get('light', '')
    chno = channel.get('siteOptions', {}).get('channelNumber', '')
    
    m3u.append(f'#EXTINF:-1 tvg-id="{cid}" tvg-chno="{chno}" tvg-logo="{logo}",{name}')
    m3u.append(stream)

with open('m3u/freelivesports.m3u', 'w', encoding='utf-8') as f:
    f.write('\n'.join(m3u))

# Generate XML
xml = [
    '<?xml version="1.0" encoding="UTF-8" ?>',
    '<!DOCTYPE tv SYSTEM "xmltv.dtd">',
    '<tv source-info-url="https://bitcentral.com" source-info-name="Bitcentral, Inc." generator-info-name="">'
]

# Add channels
for channel in data:
    if not channel: continue
    cid = channel.get('_id', '')
    name = channel.get('name', '').replace('&', '&amp;')
    logo = channel.get('thumbnails', {}).get('light', '')
    
    xml.extend([
        f'    <channel id="{cid}">',
        f'        <display-name>{name}</display-name>',
        f'        <icon src="{logo}" />',
        '    </channel>'
    ])

# Add programmes
for channel in data:
    if not channel: continue
    cid = channel.get('_id', '')
    entries = channel.get('epg', {}).get('entries', [])
    
    for entry in entries:
        if not entry: continue
        
        # Format data
        title = entry.get('title', '').replace('&', '&amp;')
        desc = entry.get('description', '').replace('&', '&amp;')
        
        # Format timestamps
        start = entry.get('start', '').replace('Z', '+00:00')
        stop = entry.get('stop', '').replace('Z', '+00:00')
        
        try:
            start_fmt = datetime.fromisoformat(start).strftime("%Y%m%d%H%M%S")
            stop_fmt = datetime.fromisoformat(stop).strftime("%Y%m%d%H%M%S")
        except:
            continue
        
        xml.extend([
            f'    <programme start="{start_fmt} +0000" stop="{stop_fmt} +0000" channel="{cid}">',
            f'        <title>{title}</title>',
            f'        <desc>{desc}</desc>',
            '    </programme>'
        ])

xml.append('</tv>')

with open('epg/freelivesports.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(xml))

print("Files generated: m3u/freelivesports.m3u and epg/freelivesports.xml")
