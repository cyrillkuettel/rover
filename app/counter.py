"""An atomic, thread-safe incrementing counter."""
import threading


class AtomicCounter:

    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.plant_count = initial
        self._lock = threading.Lock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        with self._lock:
            self.plant_count += num
            return self.plant_count

    def get_plant_count_with_lock(self):
        with self._lock:
            return self.plant_count

    def reset(self):
        with self._lock:
            self.plant_count = 0
