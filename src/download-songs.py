import json
import os
from time import sleep

songs_dir = 'songs'
downloaded_songs = [
  os.path.join(songs_dir, song) for song in os.listdir(songs_dir)
]

with open('music_tracks.json', 'r') as f:
  music_tracks = json.load(f)

for trackuri, track in music_tracks.items():
  downloaded = False
  for songfname in downloaded_songs:
    if track['yturi'] in songfname:
      downloaded = True
      break
  
  if not downloaded:
    # run youtube-dl
    print('Downloading', track['yturi'])
    ret = os.system(
      'yt-dlp -f bestaudio -x --audio-format wav -o "songs/%(id)s.%(ext)s" {}'.format(
        track['yturi']
      )
    )
    if ret != 0:
      print('Failed to download', track['yturi'])
    else:
      print('Downloaded', track['yturi'])
    sleep(500)
  else:
    print('Already downloaded', track['yturi'])
  
