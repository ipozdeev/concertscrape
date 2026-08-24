"""A tiny registry so contributors add a scraper with one decorator.

Example
-------
    from concertscrape.registry import register
    from concertscrape.scrapers.base import PageScraper

    @register("myvenue")
    class MyVenueScraper(PageScraper):
        ...

The live scrapers are registered by importing them in ``scrapers/__init__``.
"""

from __future__ import annotations

from collections.abc import Callable

# name -> zero-arg factory that returns a scraper instance
_REGISTRY: dict[str, Callable[[], object]] = {}


def register(name: str):
    """Class decorator that registers a page scraper under ``name``."""

    def _decorate(cls):
        if name in _REGISTRY:
            raise ValueError(f"scraper {name!r} is already registered")
        _REGISTRY[name] = cls
        return cls

    return _decorate


def registered_scrapers() -> dict[str, Callable[[], object]]:
    """Return a copy of the registry (name -> factory)."""
    return dict(_REGISTRY)
