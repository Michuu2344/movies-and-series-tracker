import time
import threading
from collections import defaultdict

class TokenBucket:

    def __init__(self,max_tokens : int,refill_rate : int, interval : float):

        assert max_tokens > 0
        assert refill_rate > 0
        assert interval > 0


        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.interval = interval

        self.tokens = max_tokens
        self.refilled_at = time.monotonic()
        self.lock = threading.Lock()
    def _refill(self):

        now = time.monotonic()

        elapsed = now - self.refilled_at

        if elapsed >= self.interval:
            num_refills = int(elapsed // self.interval)

            self.tokens = min(self.max_tokens,
                              self.tokens + num_refills * self.refill_rate)

            self.refilled_at += num_refills * self.interval

    def allow_requests(self,tokens : int = 1) -> bool:

        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_remaining(self) -> int:

        with self.lock:
            self._refill()
            return self.tokens
    def get_reset_time(self) -> float:
        with self.lock:
            return self.refilled_at + self.interval 

class RateLimiterStore:
    def __init__(self,max_tokens : int,refill_rate : int,interval : float):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.interval = interval
        self._bucket : dict[str, TokenBucket] = {}
        self.lock = threading.Lock()

    def get_bucket(self, key : str) ->TokenBucket:
        with self.lock:
            if key not in self._bucket:
                self._bucket[key] = TokenBucket(
                    max_tokens=self.max_tokens,
                    refill_rate=self.refill_rate,
                    interval= self.interval
                )
            return self._bucket[key]
        