import requests
import json

# Make the API request
url = "https://epg.unreel.me/v2/sites/rewardedtv/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Generate M3U content for all channels
m3u_content = "#EXTM3U url-tvg=\"https://raw.githubusercontent.com/Arkina1234/iptv-streams/main/rewardedtv.xml\"\n"
for channel in data:
    thumbnails = channel.get('thumbnails', {}).get('light')
    channel_id = channel.get('_id')
    name = channel.get('name')
    url = channel.get('url')
    
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_content += f'{url}\n'

# Generate XMLTV content for all channels
xmltv_content = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv source-info-url="https://epg.unreel.me" source-info-name="Bitcentral" generator-info-name="">
"""

# Add channels
for channel in data:
    thumbnails = channel.get('thumbnails', {}).get('light')
    channel_id = channel.get('_id')
    name = channel.get('name')
    
    xmltv_content += f"""<channel id="{channel_id}">
<display-name>{name}</display-name>
<icon src="{thumbnails}" />
</channel>
"""

# Add programmes
for channel in data:
    channel_id = channel.get('_id')
    
    # Check if EPG data exists
    if channel.get('epg') and channel['epg'].get('entries'):
        for entry in channel['epg']['entries']:
            epg_description = entry.get('description', '')
            epg_start = entry.get('start')
            epg_stop = entry.get('stop')
            epg_title = entry.get('title', '')
            
            xmltv_content += f"""<programme start="{epg_start}" stop="{epg_stop}" channel="{channel_id}">
<title lang="en">{epg_title}</title>
<desc lang="en">{epg_description}</desc>
</programme>
"""

xmltv_content += "</tv>"

# Save to files
with open('rewardedtv.m3u', 'w', encoding='utf-8') as m3u_file:
    m3u_file.write(m3u_content)

with open('rewardedtv.xml', 'w', encoding='utf-8') as xml_file:
    xml_file.write(xmltv_content)

print(f"Processed {len(data)} channels")
print("Files saved successfully:")
print("- rewardedtv.m3u")
print("- rewardedtv.xml")