# concertscrape

Scrapers that collect **upcoming classical-concert livestreams** (from YouTube
channels and a few venue websites) into a public calendar you can subscribe to.

## 📅 The calendar

- **Browse it:** https://ipozdeev.github.io/concertscrape/ — a month/week view
  that shows every concert **in your own local time** (handy for an audience
  spread from the US to China).
- **Subscribe** (new concerts then appear automatically in your own calendar):
  add the feed URL `https://ipozdeev.github.io/concertscrape/calendar.ics`
  - **Google Calendar:** Other calendars → *From URL* → paste the link.
  - **Apple Calendar:** File → *New Calendar Subscription* → paste the link.
  - **Proton Calendar:** Other calendars → *Add calendar from URL* → paste the link.
  - Or click **Subscribe** on the page (uses a `webcal://` link).

> **Why a subscription feed instead of a shared Google/Proton calendar?**
> Proton Calendar has no API or CalDAV (it's end-to-end encrypted), so it can't
> be *populated* programmatically — but it, like every other calendar app, can
> *subscribe* to an `.ics` URL. Publishing one `.ics` feed reaches everyone.

## How it works

```
scrapers (YouTube API + venue pages)  ->  Event objects  ->  calendar.ics  ->  GitHub Pages
```

1. `concertscrape run` scrapes every source and normalizes each into an
   `Event` (timezone-aware start, title, stream link).
2. It writes `docs/calendar.ics` — the canonical, subscribable feed.
3. GitHub Pages serves `docs/` (the `.ics` feed **and** the browser view in
   `docs/index.html`, which renders the feed with FullCalendar in local time).
4. A scheduled [GitHub Action](.github/workflows/scrape.yml) re-runs it every
   two days and commits the updated feed. (You can also run it from a
   RaspberryPi / any cron — see below.)

## Run it yourself

Requires [`uv`](https://docs.astral.sh/uv/) and a free **YouTube Data API v3**
key (read-only — no OAuth).

```bash
uv sync
cp .env.example .env        # then set YOUTUBE_API_KEY
uv run concertscrape run    # writes docs/calendar.ics
```

Optional flags: `--output-dir DIR`, and `--gcal` to also mirror events into a
Google Calendar (needs the `gcal` extra and OAuth credentials — see
`.env.example`).

### Hosting

Enable GitHub Pages (Settings → Pages → *Deploy from a branch* → `main` /
`/docs`). To automate updates, add a repository secret `YOUTUBE_API_KEY`; the
scheduled workflow does the rest. On a Pi instead, run the command above from
cron and `git push` the updated `docs/`.

## Contributing

Add a venue in minutes — a YouTube channel is one line in
[`channels.json`](src/concertscrape/data/channels.json); a website scraper is a
small class. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Project layout

```
src/concertscrape/
  models.py          # Event: the normalized, timezone-aware event
  cli.py             # `concertscrape run`
  youtube.py         # YouTube Data API (read-only, API key)
  registry.py        # @register decorator for scrapers
  scrapers/          # base classes + live venue scrapers (stmary, pcms)
    contrib/         # TEMPLATE + quarantined scrapers awaiting porting
  publish/           # ics_sink (canonical) + optional gcal_sink
  data/channels.json # YouTube channels to watch
docs/                # GitHub Pages: index.html + generated calendar.ics
tests/               # offline, fixture-based
```

## License

See [LICENSE](LICENSE).
