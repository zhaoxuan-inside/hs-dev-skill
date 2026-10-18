"""Byte-accounted LRU. Resident objects share the same global allocation ceiling."""

import json
from collections import OrderedDict


class ByteLRU:
    def __init__(self, maximum):
        self.maximum = maximum
        self.used = 0
        self.items = OrderedDict()

    def get(self, key):
        if key not in self.items:
            return None
        value = self.items.pop(key)
        self.items[key] = value
        return json.loads(value)

    def put(self, key, value):
        encoded = json.dumps(value, ensure_ascii=False).encode("utf-8")
        size = len(encoded) + len(key.encode("utf-8")) + 256
        if key in self.items:
            previous = self.items.pop(key)
            self.used -= len(previous) + len(key.encode("utf-8")) + 256
        if size > self.maximum:
            return
        while self.used + size > self.maximum and self.items:
            old_key, old = self.items.popitem(last=False)
            self.used -= len(old) + len(old_key.encode("utf-8")) + 256
        self.items[key] = encoded
        self.used += size

    def clear(self):
        self.items.clear()
        self.used = 0
