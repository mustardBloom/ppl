import time
import threading


class InMemoryCache:
    _lock = threading.Lock()

    def __init__(self, expiration_time: int = 300):
        """
        Initialize the cache with an optional expiration time.
        
        :param expiration_time: Time in seconds before cache entries expire (default: 300 seconds).
        """
        self.cache = {}
        self.expiration_time = expiration_time

    def set(self, key, value, expired_at: int = None):
        """
        Store a value in the cache with the current timestamp.
        
        :param key: Cache key.
        :param value: Value to cache.
        """
        with self._lock:
            self.cache[key] = {
                "value": value,
                "expired_at": time.time() + self.expiration_time if expired_at is None else expired_at
            }

    def get(self, key):
        """
        Retrieve a value from the cache if it's still valid.
        
        :param key: Cache key.
        :return: Cached value or None if not found or expired.
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() > entry["expired_at"]:
            # Expired, remove from cache
            del self.cache[key]
            return None

        return entry["value"]

    def delete(self, key):
        """
        Remove a value from the cache.
        
        :param key: Cache key to remove.
        """
        with self._lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear the entire cache."""
        with self._lock:
            self.cache.clear()

    def __repr__(self):
        return f"<InMemoryCache size={len(self.cache)}>"
