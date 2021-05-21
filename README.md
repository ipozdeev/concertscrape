# concertscrape
web scrapers for live streams of classical concerts

## intro
implements scrapers to collect events appearing in [my calendar](https://calendar.google.com/calendar/embed?src=nribadjfkdu40so2bc8tc92v5k%40group.calendar.google.com&ctz=Europe%2FZurich).

scrapers are venue-specific; if you want to contribute, feel free to implement 
one for your venue of choice by subclassing class `PageScraper` or adding a 
line to `YoutubeScraper.NAME_MAP` in `core.py`. 
