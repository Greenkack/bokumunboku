"""
Small file-based cache for PVGIS API results.

This cache stores PVGIS responses in JSON format keyed by a SHA-256
hash of the request parameters. The cache directory is created
automatically if it does not exist. Entries expire after a defined
time-to-live (TTL), avoiding stale results. Integrate this cache
into your PVGIS request function by checking `get_cached` before
making an HTTP request and calling `set_cached` after obtaining
fresh results.

Usage example:

    from enhancements.pvgis_cache import get_cached, set_cached

    def fetch_pvgis(params: dict) -> dict:
        cached = get_cached(params)
        if cached is not None:
            return cached
        data = actually_request_pvgis(params)  # Your existing function
        set_cached(params, data)
        return data
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Directory to store cache files (relative to this file)
_CACHE_DIR = Path(__file__).resolve().parent / '.cache'
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Time-to-live for cache entries (in seconds). Adjust as needed.
_TTL_SECONDS = 6 * 3600  # 6 hours


def _key(params: Dict[str, Any]) -> str:
    """Compute a cache file name based on request parameters."""
    # Serialize parameters deterministically by sorting keys
    params_serialized = json.dumps(params, sort_keys=True).encode('utf-8')
    digest = hashlib.sha256(params_serialized).hexdigest()
    return f'{digest}.json'


def get_cached(params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return cached data for given parameters if available and not expired."""
    cache_path = _CACHE_DIR / _key(params)
    if not cache_path.exists():
        return None
    # If file is older than TTL, ignore it
    age = time.time() - cache_path.stat().st_mtime
    if age > _TTL_SECONDS:
        return None
    try:
        return json.loads(cache_path.read_text(encoding='utf-8'))
    except Exception:
        return None


def set_cached(params: Dict[str, Any], data: Dict[str, Any]) -> None:
    """Write data to the cache for given parameters."""
    cache_path = _CACHE_DIR / _key(params)
    try:
        cache_path.write_text(json.dumps(data), encoding='utf-8')
    except Exception:
        # Ignore write errors silently; caching is a performance optimization
        pass