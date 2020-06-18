import hashlib


def get_hash(obj):
    if isinstance(obj, dict):
        text = obj["title"]
    else:
        text = obj
    return hashlib.md5(text.encode("utf-8")).hexdigest()
