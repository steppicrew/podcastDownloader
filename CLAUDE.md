# CLAUDE.md

Guidance for working in this repo.

## What this is

A downloader for ARD Audiothek podcasts (ardsounds.de / ardaudiothek.de).
`download.py` rips every episode of a show as `<NN> <title>.mp3` into a folder
named after the podcast.

## How it works

- Episodes are **not** in the page HTML (HTML has only page 1). The real source is
  the GraphQL endpoint `https://api.ardaudiothek.de/graphql`, operation
  `ProgramSetEpisodesQuery` (GET, params `query` + `variables`).
- `variables = {"id": "<urn:ard:show:...>", "offset": N, "count": M}`; paginate via
  `pageInfo.hasNextPage`. Needs a `Referer: https://www.ardsounds.de/` header, no auth.
- Each node has `title`, `programSet.title` (folder name), and
  `audios[].downloadUrl` (direct `.mp3`).
- `NN` = the `Folge NN` number parsed from the title, zero-padded to 2 digits.
  Items without a Folge number (trailers, feed promos) are skipped.

## Usage

```sh
python3 download.py '<show-url-or-urn>' [output-dir]
```

Per-podcast wrapper scripts hardcode the show URL, e.g.:

```sh
./professor-van-dusen.sh
```

Adding a new podcast: copy a wrapper `.sh`, swap in the show's ardsounds URL.

## Notes

- **Idempotent.** Re-running skips files already present and writes via a `.part`
  temp, so it only fetches new or missing episodes. Safe to re-run for new releases.
- Downloaded `*.mp3` files are gitignored.
- Stdlib only (no pip deps); needs Python 3.

## Type checking

`download.py` is fully annotated and passes `mypy --strict` cleanly. Keep it that
way: run `mypy --strict download.py` after changes. The dynamic JSON from the API is
typed as `dict[str, Any]`; when returning values pulled out of it, assign to a typed
local first to avoid `no-any-return` errors. (pyright should also be clean — same
annotations — but isn't installed in this environment.)
