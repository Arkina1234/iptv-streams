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

# Process the first channel
channel = data[0]

# Extract channel information
epg_description = channel.get('epg', {}).get('entries', [{}])[0].get('description') if channel.get('epg', {}).get('entries') else None
epg_start = channel.get('epg', {}).get('entries', [{}])[0].get('start') if channel.get('epg', {}).get('entries') else None
epg_stop = channel.get('epg', {}).get('entries', [{}])[0].get('stop') if channel.get('epg', {}).get('entries') else None
epg_title = channel.get('epg', {}).get('entries', [{}])[0].get('title') if channel.get('epg', {}).get('entries') else None
thumbnails = channel.get('thumbnails', {}).get('light')
channel_id = channel.get('_id')
name = channel.get('name')
stream_url = channel.get('url')

# Process EPG data
description = html.escape(epg_description) if epg_description else ""
start = datetime.strptime(epg_start, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S") if epg_start else ""
stop = datetime.strptime(epg_stop, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H%M%S") if epg_stop else ""
title = html.escape(epg_title) if epg_title else ""

# Process stream URL
stream = stream_url.replace('[', '%5B').replace(']', '%5D') if stream_url else ""

# Generate M3U output
m3u_output = f"""#EXTM3U
#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{thumbnails}",{name}
{stream}
"""

# Generate XMLTV output
tv = ET.Element("tv")
tv.set("source-info-url", "https://epg.unreel.me")
tv.set("source-info-name", "Bitcentral")
tv.set("generator-info-name", "")

# Channel element
channel_elem = ET.SubElement(tv, "channel")
channel_elem.set("id", channel_id)

display_name = ET.SubElement(channel_elem, "display-name")
display_name.text = html.escape(name)

icon = ET.SubElement(channel_elem, "icon")
icon.set("src", thumbnails)

# Programme element (if EPG data exists)
if epg_start and epg_stop:
    programme = ET.SubElement(tv, "programme")
    programme.set("start", f"{start} +0000")
    programme.set("stop", f"{stop} +0000")
    programme.set("channel", channel_id)

    title_elem = ET.SubElement(programme, "title")
    title_elem.set("lang", "en")
    title_elem.text = title

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

print("Files saved successfully!")
print("M3U file: fmplus.m3u")
print("XML file: fmplus.xml")