# Center videos

All videos are rendered from the center's own records, frame by frame, in a headless browser.

- `loop.html`: the 40-second loop explainer (media/center-loop.mp4 and the vertical cut)
- `engine.html`: the general video engine (titles, bullet reveals, counters, bar charts, the growing
  collaboration graph, Ken Burns photos, people, cards, end cards) in 16:9 or 9:16
- `storyboards.py`: builds every storyboard from build_site.py's records and writes one HTML per video
- `renderall.py`: renders the frames at 24 fps, resumably, and encodes each video with ffmpeg

To make a "paper in 30 seconds" for a new paper, add it to the list in storyboards.py (it must have a
verified problem and finding in acnl_records.json), rerun the two scripts, and copy the MP4 and poster
into media/v/. media/videos.json holds each video's transcript for the site.
