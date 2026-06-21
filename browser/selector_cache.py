"""
Self-healing selector cache for the Voice Browser Agent.

Caches the selector that last *worked* for a logical element on a given domain,
keyed by (domain, label). On the next interaction the cached selector is tried
first; if it still works there's no need to re-derive it. If it breaks, the
caller falls back to fresh selectors and the cache self-heals with the new
winner. This is the Stagehand-style pattern: reason about the element once,
reuse the resolved selector deterministically, re-engage only on failure.

The cache persists to data/selector_cache.json so repeat tasks across runs
skip selector rediscovery entirely.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import config
from utils.logger import log_browser_debug, log_browser_warning


def domain_of(url: str) -> str:
    """Return a normalized domain key (lowercased, no leading 'www.')."""
    try:
        netloc = urlparse(url or "").netloc.lower()
    except Exception:
        return ""
    return netloc[4:] if netloc.startswith("www.") else netloc


class SelectorCache:
    """Persistent {domain: {label: selector}} cache of working selectors."""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else Path(config.DATA_DIR) / "selector_cache.json"
        self._data: Dict[str, Dict[str, str]] = self._load()

    def _load(self) -> Dict[str, Dict[str, str]]:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            log_browser_warning(f"Selector cache unreadable, starting fresh: {e}")
            return {}

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_browser_warning(f"Could not persist selector cache: {e}")

    def get(self, domain: str, label: str) -> Optional[str]:
        """Return the cached working selector for (domain, label), if any."""
        if not domain or not label:
            return None
        return (self._data.get(domain) or {}).get(label)

    def put(self, domain: str, label: str, selector: str) -> None:
        """Record a selector that just worked for (domain, label)."""
        if not domain or not label or not selector:
            return
        if self._data.get(domain, {}).get(label) == selector:
            return  # unchanged; avoid a needless write
        self._data.setdefault(domain, {})[label] = selector
        log_browser_debug(f"Cached selector '{label}'@{domain} -> {selector}")
        self._save()

    def invalidate(self, domain: str, label: str) -> None:
        """Drop a stale entry (e.g. when a cached selector stops working)."""
        if self._data.get(domain, {}).pop(label, None) is not None:
            self._save()
