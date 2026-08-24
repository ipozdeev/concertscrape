"""Live venue scrapers.

Importing this package registers every live scraper in the registry. To add a
venue: create a module here, decorate the class with ``@register("name")``, and
import it below. See ``contrib/TEMPLATE.py`` for a starting point.
"""

from . import pcms, stmary  # noqa: F401  (imported for their @register side effects)

__all__ = ["pcms", "stmary"]
