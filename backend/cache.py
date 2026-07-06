"""
Thread-safe 인메모리 TTL 캐시
- 같은 종목 반복 요청 시 yfinance / Claude 재호출 방지
- 나중에 Redis로 교체 가능
"""
import time
import threading
from typing import Any, Optional


class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, ttl: int = 300) -> Optional[Any]:
        with self._lock:
            if key not in self._store:
                return None
            val, ts = self._store[key]
            if time.time() - ts > ttl:
                del self._store[key]
                return None
            return val

    def set(self, key: str, val: Any):
        with self._lock:
            self._store[key] = (val, time.time())

    def delete(self, key: str):
        with self._lock:
            self._store.pop(key, None)


cache = TTLCache()
