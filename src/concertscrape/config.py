"""Typed settings loaded from the environment (optionally via a .env file).

Replaces the old ``from config import *`` star-import. Import ``settings`` for a
lazily-populated singleton, or call ``load_settings()`` for a fresh read.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv


@dataclass(frozen=True)
class Settings:
    # --- YouTube (read-only public data -> a simple API key is enough) ---
    youtube_api_key: str | None = None

    # --- Output ---
    # Directory the .ics feed (and any generated site assets) are written to.
    # Defaults to <repo>/docs so GitHub Pages can serve it.
    output_dir: str = "docs"

    # --- Optional Google Calendar mirror ---
    calendar_id: str | None = None
    google_creds_file: str | None = None  # OAuth client secrets json

    # --- Optional log email digest ---
    log_email_to: str | None = None
    log_email_from: str | None = None

    @property
    def gcal_enabled(self) -> bool:
        return bool(self.calendar_id and self.google_creds_file)


def load_settings() -> Settings:
    """Read settings from the environment, loading a .env file if present."""
    load_dotenv(find_dotenv(usecwd=True))
    return Settings(
        youtube_api_key=os.environ.get("YOUTUBE_API_KEY"),
        output_dir=os.environ.get("OUTPUT_DIR", "docs"),
        calendar_id=os.environ.get("CALENDAR_ID"),
        google_creds_file=os.environ.get("GOOGLE_CREDS_FILE"),
        log_email_to=os.environ.get("LOG_EMAIL_TO"),
        log_email_from=os.environ.get("LOG_EMAIL_FROM"),
    )


settings = load_settings()
