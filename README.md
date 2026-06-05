# podcastDownloader

[![mypy](https://github.com/steppicrew/podcastDownloader/actions/workflows/mypy.yml/badge.svg)](https://github.com/steppicrew/podcastDownloader/actions/workflows/mypy.yml)

Download all episodes of an [ARD Audiothek](https://www.ardaudiothek.de/) podcast
(ardsounds.de / ardaudiothek.de) as MP3 files.

Each episode is saved as `<NN> <title>.mp3` inside a folder named after the
podcast, where `NN` is the zero-padded *Folge* (episode) number.

## Requirements

- Python 3 (standard library only — no `pip` dependencies)

## Usage

```sh
python3 download.py '<show-url-or-urn>' [output-dir]
```

`<show-url-or-urn>` can be a full ardsounds.de URL or a bare `urn:ard:show:...`.
`output-dir` defaults to the current directory.

Example:

```sh
python3 download.py 'https://www.ardsounds.de/sendung/professor-van-dusen/urn:ard:show:8103e24c954e0404/'
```

### Per-podcast wrapper scripts

Wrapper scripts hardcode a show's URL for convenience:

```sh
./professor-van-dusen.sh
```

To add another podcast, copy a wrapper `.sh` and swap in the show's ardsounds.de URL.

## Notes

- **Idempotent.** Re-running skips files already present (it downloads to a `.part`
  temp file first), so it only fetches new or missing episodes. Safe to re-run when
  new episodes are released.
- Trailers and feed promos (titles without a *Folge* number) are skipped.
- Downloaded `*.mp3` files are gitignored.

## How it works

Episodes are not in the page HTML (only the first page is). The real source is the
GraphQL endpoint `https://api.ardaudiothek.de/graphql` (operation
`ProgramSetEpisodesQuery`), which is paginated to collect every episode and its
direct MP3 download URL.
