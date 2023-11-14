# Lyrics

download from Spotify

# Song

download from Youtube Music

### Script

using `yt-dlp` to download from Youtube Music

```bash
yt-dlp -f bestaudio -x --audio-format wav -o "songs/%(id)s.%(ext)s" <url|id>
```
