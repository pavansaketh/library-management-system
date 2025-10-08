import time
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class OpenLibraryClient:
    BASE = "https://openlibrary.org"

    def __init__(self, rate_limit_seconds: float = 1.0, timeout: float = 10.0, max_retries: int = 3):
        self.rate_limit_seconds = rate_limit_seconds
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._last_request_ts = 0.0

    def _sleep_if_needed(self):
        elapsed = time.time() - self._last_request_ts
        if elapsed < self.rate_limit_seconds:
            to_sleep = self.rate_limit_seconds - elapsed
            logger.debug("Rate limiting: sleeping %.3f seconds", to_sleep)
            time.sleep(to_sleep)

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE}{path}"
        attempt = 0
        while True:
            attempt += 1
            self._sleep_if_needed()
            try:
                logger.debug("Requesting %s params=%s (attempt %d)", url, params, attempt)
                resp = self._session.get(url, params=params, timeout=self.timeout)
                self._last_request_ts = time.time()
                if resp.status_code == 200:
                    return resp.json()
                elif 500 <= resp.status_code < 600:
                    logger.warning("Server error %s on %s (attempt %d)", resp.status_code, url, attempt)
                else:
                    logger.error("HTTP error %s for %s: %s", resp.status_code, url, resp.text[:400])
                    resp.raise_for_status()
            except requests.RequestException as e:
                logger.warning("RequestException for %s (attempt %d): %s", url, attempt, e)
            if attempt >= self.max_retries:
                raise RuntimeError(f"Failed to fetch {url} after {self.max_retries} attempts")
            backoff = 0.5 * attempt
            logger.debug("Backing off for %.2f seconds before retry", backoff)
            time.sleep(backoff)

    def search_authors(self, author_name: str, limit: int = 10) -> Dict[str, Any]:
        path = "/search/authors.json"
        params = {"q": author_name, "limit": limit}
        return self._request(path, params=params)

    def get_author_works(self, author_key: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        path = f"/authors/{author_key}/works.json"
        params = {"limit": limit, "offset": offset}
        return self._request(path, params=params)

    def get_work_detail(self, work_key: str) -> Dict[str, Any]:
        key = work_key.strip().rstrip("/").split("/")[-1]
        path = f"/works/{key}.json"
        return self._request(path)


    def close(self):
        self._session.close()
