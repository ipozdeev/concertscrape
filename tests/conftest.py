from pathlib import Path

import pytest
from bs4 import BeautifulSoup

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_soup():
    """Return a callable that loads a fixture HTML file as BeautifulSoup."""

    def _load(name: str) -> BeautifulSoup:
        html = (FIXTURES / name).read_text(encoding="utf-8")
        return BeautifulSoup(html, "html.parser")

    return _load
