# utils/response_picker.py
import json
import random

_cache = {}

def get_random_response(filepath):
    if filepath not in _cache:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = json.load(f)
        random.shuffle(lines)
        _cache[filepath] = {"lines": lines, "index": 0}

    entry = _cache[filepath]
    response = entry["lines"][entry["index"]]
    entry["index"] += 1

    if entry["index"] >= len(entry["lines"]):
        random.shuffle(entry["lines"])
        entry["index"] = 0

    return response
