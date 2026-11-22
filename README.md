# The World — 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/lively-raven-87/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/lively-raven-87/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

One 1024×1024 newspaper front page for 22 November 2026. The COP31
climate summit in Antalya ending with no deal leads the page; below it,
Iran's strikes on Bahrain, a Russian drone attack on Dymer, the capture
of "El Chapo Isidro" in Sinaloa, and global markets sliding into
correction, with a ticker of the day's other stories along the bottom.

Entered on [make.fun](https://make.fun/?ref=200tdmdd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards

## What's here

- `draw.py` — paints the front page with Pillow; run `python3 draw.py`
  and it writes `entry.png` beside itself.
- `main.py` — the deliverable, stdlib only: it checks `entry.png` is a
  whole PNG (signature, every chunk's CRC, 1024×1024, at most 1 MiB) and
  copies it to `/output/entry.png`.
- `entry.png` — the finished front page.

## Run

```sh
python3 draw.py   # paint entry.png
python3 main.py   # check it, then copy to /output/entry.png
```
