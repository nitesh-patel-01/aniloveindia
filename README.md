# AniLove India

Static anime, anime movie, Hindi movie and K-drama website using official YouTube embeds.

Production target: https://aniloveindia.vercel.app

## Build

Run `python3 build.py`. Output is `dist/`. No dependencies or API keys are required to build or browse the existing catalogue. Vercel reads `vercel.json` and builds from the GitHub main branch.

## Checks

```sh
python3 scripts/audit.py
python3 -m unittest discover -s tests
node --check assets/app.js
```

## Features

- 119 title entries and 548 checked official video uploads
- Season tabs, episode thumbnails, exact-video pages and fullscreen YouTube playback
- Simple search and browser-local watchlist
- Requests open WhatsApp to +91 79748 23298; visitors review and send the message
- Six search landing pages with canonical metadata, visible FAQs, structured data and sitemap entries

YouTube uploaders control regional availability. India appears in source country metadata, but actual India playback is unverified. Complete seasons are not universally certified.

## Catalogue maintenance

`data/channels.json` retains reviewed uploader identities. Verification and discovery scripts are in `scripts/`. The daily workflow is manual-only until API access is configured and tested; no automatic daily discovery is active. Put a YouTube API key in GitHub Actions secrets as `YOUTUBE_API_KEY`, never in source.

Videos stay on YouTube. This repository contains metadata and player pages, not video downloads.
