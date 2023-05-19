# global_registry.py
from collections import defaultdict

# This is a map of WebSocket session IDs to consumers
websockets = defaultdict(dict)