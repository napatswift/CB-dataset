import librosa
import soundfile as sf
import os
import json
import pandas as pd
from tqdm import tqdm

dataset_dir = 'dataset'
dataset_audio_dir = 'data'


class LyricLine:
    def __init__(self, words, startTimeMs, endTimeMs):
        self.words = words

        self.startTimeMs = startTimeMs
        if isinstance(startTimeMs, str):
            self.startTimeMs = int(startTimeMs)
        assert isinstance(self.startTimeMs, (int, float)
                          ), type(self.startTimeMs)

        self.endTimeMs = endTimeMs
        if isinstance(endTimeMs, str):
            self.endTimeMs = int(endTimeMs)
        assert isinstance(self.endTimeMs, (int, float))

        self.audiopath = ''

    def __str__(self,):
        return f'LyricLine({self.words})'

    def startTimeSecs(self):
        return self.startTimeMs / 1000

    def endTimeSecs(self):
        return self.endTimeMs / 1000

    def durationSecs(self,):
        return self.endTimeSecs() - self.startTimeSecs()

    def setAudioPath(self, audiopath):
        self.audiopath = audiopath

    def to_dict(self,):
        return dict(
            audiopath=self.audiopath,
            words=self.words
        )


def create_chunks(lyric_lines):
    first_line = {
        'startTimeMs': '0',
        'words': "",
        'endTimeMs': '0'
    }

    lyric_lines = [first_line] + lyric_lines

    chunks = []
    for chunk_len in range(1, 3):
        for startidx in range(len(lyric_lines) - chunk_len):
            endidx = startidx + chunk_len
            start = lyric_lines[startidx]
            end = lyric_lines[endidx]
            words = '\t'.join([
                l['words'] for l in lyric_lines[startidx:endidx]
                if l['words']
            ])
            chunks.append(
                LyricLine(words, start['startTimeMs'], end['startTimeMs']))
    return chunks


def write_chunks(chunks, track_path):
    for chunk in chunks:
        wav, sr = librosa.load(track_path,
                               offset=chunk.startTimeSecs(),
                               duration=chunk.durationSecs())
        file_name = f'{hex(hash(wav.tobytes()))[2:]}.wav'
        save_path = os.path.join(dataset_dir, dataset_audio_dir, file_name)
        file_path = os.path.join(dataset_audio_dir, file_name)
        sf.write(save_path, wav, sr)
        chunk.setAudioPath(file_path)


def to_dict(obj):
    if isinstance(obj, list):
        return [o.to_dict() for o in obj]
    return obj.to_dict()


def list_of_songs(path):
    songs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".wav"):
                songs.append(os.path.join(root, file))
    return songs


def find_sound_file(yt_id, downloaded_sound_files):
    for file in downloaded_sound_files:
        if yt_id in file:
            return file
    return None


if __name__ == '__main__':
    if not os.path.exists(os.path.join(dataset_dir, dataset_audio_dir)):
        os.makedirs(os.path.join(dataset_dir, dataset_audio_dir))

    tracks = json.load(open('music_tracks.json'))
    downloaded_sound_files = list_of_songs('songs')
    all_lyric_lines = []
    for trackid in tqdm(tracks):
        track = tracks[trackid]
        chunks = create_chunks(track['lyrics']['lines'])

        track_path = find_sound_file(track['yturi'], downloaded_sound_files)
        if track_path is None:
            continue

        write_chunks(chunks, track_path)

        all_lyric_lines += chunks

        track['lyric_lines'] = chunks

        pd.DataFrame(to_dict(all_lyric_lines),)\
            .rename(columns={'audiopath': 'file_name'})\
            .to_csv(os.path.join(dataset_dir, 'metadata.csv',), index=False)
