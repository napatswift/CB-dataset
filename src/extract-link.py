from bs4 import BeautifulSoup
import re
import urllib.parse
import os
import json

yttracks_path = 'yttracks.json'
file_paths = os.listdir('ytmusic')
file_paths = [os.path.join('ytmusic', file_path) for file_path in file_paths]

tracks = {} # {trackname: track yt uri}
if os.path.exists(yttracks_path):
    with open(yttracks_path, 'r') as f:
        tracks = json.load(f)

for file_path in file_paths:
    with open(file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

        page_tracks = soup.find_all('a', {
            'class': 'yt-simple-endpoint'
        })

        for track in page_tracks:
            href = track['href']
            if not href.startswith('watch'): continue
            search_params = urllib.parse.parse_qs(urllib.parse.urlparse(track['href']).query)
            if 'v' in search_params:
                tracks[re.sub(r'\s+', ' ', track.text)] = search_params['v'][0]
            else:
                print('No video found for', track.text)

with open(yttracks_path, 'w') as f:
    json.dump(tracks, f, indent=4)