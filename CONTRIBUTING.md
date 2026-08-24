# Contributing

Thanks for helping grow the classical-livestream calendar! There are two kinds
of sources you can add.

## 1. Add a YouTube channel (easiest)

Most venues just stream to YouTube. Find the channel's **channel ID** (starts
with `UC…`; see the channel's page source or a tool like *ytinitialdata*), then
add one line to
[`src/concertscrape/data/channels.json`](src/concertscrape/data/channels.json):

```json
"my venue": "UCxxxxxxxxxxxxxxxxxxxxxx"
```

That's it — upcoming livestreams on that channel are picked up automatically.

## 2. Add a venue website scraper

For venues that stream elsewhere (their own site, Vimeo, etc.), write a small
scraper.

1. Copy [`src/concertscrape/scrapers/contrib/TEMPLATE.py`](src/concertscrape/scrapers/contrib/TEMPLATE.py)
   to `src/concertscrape/scrapers/<venue>.py`.
2. Implement the two methods (see `stmary.py` / `pcms.py` for working examples):
   - `get_upcoming_livestreams()` → list of items (usually event-page URLs).
   - `get_livestream_details(item)` → `{"start", "summary", "description"}`,
     where **`start` is a naive `datetime` in the venue's local time**. The base
     class localizes it with the venue timezone you pass to `super().__init__`.
3. Decorate the class with `@register("<name>")`.
4. Register it by importing it in
   [`src/concertscrape/scrapers/__init__.py`](src/concertscrape/scrapers/__init__.py).
5. Add an **offline test** with a saved HTML fixture (see `tests/fixtures/` and
   `tests/test_scrapers.py`) so the parser is checked without hitting the network.

### The `Event` contract

Every scraper produces `concertscrape.models.Event` objects (the base class
builds them for you). Events must have a **timezone-aware** start so they render
correctly in every viewer's local time. End defaults to +90 min; a stable UID is
derived from the URL.

## Reviving a quarantined scraper

`src/concertscrape/scrapers/contrib/needs_porting/legacy.py` holds venue scrapers
written for an older interface (they return `start` as a
`{"dateTime", "timeZone"}` dict via `get_event_schedule()`/`_get_event()`). To
revive one, port it to the current interface as described above. The venue sites
have changed since 2021, so expect to update the CSS selectors.

## Dev setup

```bash
uv sync                 # install
uv run pytest           # run offline tests
uv run ruff check .     # lint
uv run concertscrape run --output-dir /tmp/out   # try it (needs YOUTUBE_API_KEY)
```
