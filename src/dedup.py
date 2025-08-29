import time

class Deduplicator:
    def __init__(self, expiry=3600):
        self._processed_ids = {}
        self._expiry = expiry

    def is_duplicate(self, msg_id):
        now = time.time()
        expired = [k for k, v in self._processed_ids.items() if now - v > self._expiry]
        for k in expired:
            del self._processed_ids[k]
        return msg_id in self._processed_ids

    def mark_processed(self, msg_id):
        self._processed_ids[msg_id] = time.time()
