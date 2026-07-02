# New Hope YouTube Viewer Demo

This is a very plain Cloudflare Pages demo site for testing a clean YouTube viewer window.

## Purpose

The page embeds a YouTube stream/video in a simple 16:9 viewer and keeps the surrounding page uncluttered.

It does not change the church's OBS, Stream Agent, persistent stream key, or YouTube streaming workflow.

## Files

- `index.html` - the complete demo web page

## Setup

1. Find the YouTube video ID for the test channel's scheduled or active livestream.
2. Open `index.html`.
3. Replace both instances of `TEST_VIDEO_ID_HERE` with that video ID.
4. Commit the file to GitHub.
5. Connect the GitHub repository to Cloudflare Pages.

## Cloudflare Pages build settings

For this simple static site:

- Framework preset: None
- Build command: leave blank
- Build output directory: `/`

## Autoplay note

The embedded player asks YouTube to autoplay, but most browsers block automatic playback with sound.
The demo uses `mute=1` because muted autoplay is much more reliable.
A viewer may need to click the speaker icon or player controls to hear sound.
