import json
import re

tracks = {}
with open('yttracks.json', 'r') as f:
    tracks = json.load(f)

normalize_re = re.compile(r'[\[\]\(\)\-]')

new_tracks = {}
for track_name, track_uri in tracks.items():
    new_tracks[re.sub(normalize_re, '', track_name.lower())] = track_uri

tracks.update(new_tracks)

with open('tracks.json', 'r') as f:
    lyric_tracks = json.load(f)
    lyric_tracks = {t:v for t,v in lyric_tracks.items() if 'lyrics' in v}

with_yt = 0
music_tracks = {} # final
for track_uri, track in lyric_tracks.items():
    track_name = track['name']
    if 'lyrics' in track:
        yturi = tracks.get(re.sub(normalize_re, '', track_name.lower()))
        if yturi:
            track['yturi'] = yturi
            with_yt += 1
            music_tracks[track_uri] = {
                'name': track_name,
                'yturi': yturi,
                'yturl': 'https://youtu.be/' + yturi,
                'lyrics': track['lyrics']
            }
    print('>>>' if yturi is None else '***',track_name, yturi)

print(f'{with_yt}/{len(lyric_tracks)} tracks with yt uri')

with open('music_tracks.json', 'w') as f:
    json.dump(music_tracks, f, indent=2)