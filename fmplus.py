import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html

# Make the API request
url = "https://epg.unreel.me/v2/sites/fmplus/live-channels/public/081f73704b56aaceb6b459804761ec54"
response = requests.get(url)
data = response.json()

# Initialize outputs
m3u_output = "#EXTM3U url-tvg=\"https://arkina1234.github.io/iptv-streams/fmplus.xml\"\n"
tv = ET.Element("tv")
tv.set("source-info-url", "https://epg.unreel.me")
tv.set("source-info-name", "Bitcentral")
tv.set("generator-info-name", "")

# Process all channels
for channel in data:
    # Extract channel information
    thumbnails = channel.get('thumbnails', {}).get('light')
    channel_id = channel.get('_id')
    name = channel.get('name')
    stream_url = channel.get('url')

    # Process stream URL
    if stream_url:
        stream = stream_url.replace('[', '%5B').replace(']', '%5D')
    else:
        stream = ""

    # Add to M3U output
    m3u_output += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}\n'
    m3u_output += f'{stream}\n'

    # Create channel element in XML
    channel_elem = ET.SubElement(tv, "channel")
    channel_elem.set("id", channel_id)

    display_name = ET.SubElement(channel_elem, "display-name")
    display_name.text = html.escape(name)

    if thumbnails:
        icon = ET.SubElement(channel_elem, "icon")
        icon.set("src", thumbnails)

    # Process all EPG entries for this channel
    if channel.get('epg') and channel['epg'].get('entries'):
        for entry in channel['epg']['entries']:
            epg_description = entry.get('description')
            epg_start = entry.get('start')
            epg_stop = entry.get('stop')
            epg_title = entry.get('title')

            # Skip if no start/stop times
            if not epg_start or not epg_stop:
                continue

            # Process EPG data
            description = html.escape(epg_description) if epg_description else ""
            title = html.escape(epg_title) if epg_title else ""

            try:
                start = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
                stop = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S")
            except ValueError:
                continue  # Skip if date parsing fails

            # Create programme element
            programme = ET.SubElement(tv, "programme")
            programme.set("start", f"{start} +0000")
            programme.set("stop", f"{stop} +0000")
            programme.set("channel", channel_id)

            if title:
                title_elem = ET.SubElement(programme, "title")
                title_elem.set("lang", "en")
                title_elem.text = title

            if description:
                desc_elem = ET.SubElement(programme, "desc")
                desc_elem.set("lang", "en")
                desc_elem.text = description

# Convert XML to string
xml_str = ET.tostring(tv, encoding='utf-8', method='xml')
parsed_xml = minidom.parseString(xml_str)
xml_output = parsed_xml.toprettyxml(indent="  ")

# Save to files
with open("fmplus.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_output)

with open("fmplus.xml", "w", encoding="utf-8") as f:
    f.write(xml_output)

print(f"Files saved successfully!")
print(f"Processed {len(data)} channels")
print("M3U file: fmplus.m3u")
print("XML file: fmplus.xml")