import json
import re
import urllib.parse

lyric_file_paths = [
    'synclyrics/lyrics-1989.har',
    'synclyrics/lyrics-reputation.har',
    'synclyrics/lyrics-taylor-all.har',
]

def find_obj_of(type, jsonobj, tracks):
    if isinstance(jsonobj, dict) and jsonobj.get('__typename') == type:
        tracks.append(jsonobj.copy())
    else:
        if isinstance(jsonobj, dict):
            for k, v in jsonobj.items():
                find_obj_of(type, v, tracks)
        elif isinstance(jsonobj, list):
            for v in jsonobj:
                find_obj_of(type, v, tracks)

lyrics = {}
tracks = {}
all_tracks = []
for lyric_file_path in lyric_file_paths:
    print('Processing {}'.format(lyric_file_path))
    with open(lyric_file_path) as lyric_file:
        lyric_data = json.load(lyric_file)
        for entry in lyric_data['log']['entries']:
            if entry['response']['content'].get('text') and entry['response']['content'].get('mimeType') == 'application/json':
                try:
                    jsonobj = json.loads(entry['response']['content']['text'])
                    find_obj_of('Track', jsonobj, all_tracks)
                    albums = []
                    find_obj_of('Album', jsonobj, albums)
                    if albums:
                        print('Found {} albums'.format(len(albums)))
                        for album in albums:
                            if album.get('tracks', {}).get('items'):
                                for track in album['tracks']['items']:
                                    all_tracks.append(track['track'])
                except Exception as e:
                    print('Error parsing json: {}'.format(entry['response']['content']['text']))
                    continue

            if ('spclient.wg.spotify.com/color-lyrics' in entry['request']['url']
                and entry['response']['status'] == 200
                    and entry['response']['content'].get('text')):
                song_id = re.search(
                    r'track/(\w+)/', entry['request']['url']).group(1)
                lyrics[song_id] = json.loads(
                    entry['response']['content']['text'])

            continue

tracks = {track['uri']: track for track in all_tracks if track and track.get('uri')}

print('Found {} lyrics'.format(len(lyrics)))
print('Found {} tracks'.format(len(tracks)))

for trackid, lyric in lyrics.items():
    trackuri = 'spotify:track:{}'.format(trackid)
    if trackuri not in tracks:
        print('Lyric {} not found in tracks'.format(trackuri))
        continue
    if 'lyrics' in lyric:
        tracks[trackuri].update(lyric)
    else:
        tracks[trackuri]['lyrics'] = lyric

    # tracks[trackid]['lyrics'] = lyric
with open(lyric_file_path+'---tracks.json', 'a') as tracks_file:
    json.dump(all_tracks, tracks_file, indent=2)

with open('lyrics.json', 'w') as lyrics_file:
    json.dump(lyrics, lyrics_file, indent=2)

with open('tracks.json', 'w') as tracks_file:
    json.dump(tracks, tracks_file, indent=2)