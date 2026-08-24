"""Scrapers written against the OLD interface -- NOT run live, need porting.

These venue scrapers were written for an earlier design where a scraper exposed
``get_event_schedule()`` + ``_get_event(url)`` and returned ``start`` as a
``{"dateTime": ..., "timeZone": ...}`` dict. The current design (see
``concertscrape.scrapers.base.PageScraper``) instead expects:

* ``get_upcoming_livestreams()`` -> list of items, and
* ``get_livestream_details(item)`` -> ``{"start": <naive datetime>, "summary",
  "description"}``  (the base class localizes and builds an ``Event``).

To revive one: rename the two methods, return a *naive* datetime under
``"start"`` (drop the dict/timezone wrapper -- the base localizes with
``self.tz``), decorate the class with ``@register("name")``, import it from
``concertscrape.scrapers.__init__``, and add a fixture-based test. The venue
sites have also changed since 2021, so the CSS selectors likely need updating.

Kept verbatim below so the prior parsing work is not lost.
"""
