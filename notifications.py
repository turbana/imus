import hashlib
import os
import os.path
import re
import time


CACHE_DIR = "cache"


def notify(msg):
    if not should_notify(msg):
        return
    touch(os.path.join(CACHE_DIR, get_hash(msg)))
    print(msg)


def should_notify(msg):
    filename = os.path.join(CACHE_DIR, get_hash(msg))
    if os.path.exists(filename):
        mtime = os.stat(filename).st_mtime
        delta = time.time() - mtime
        max_time = parse_time(msg["options"]["suppress_time"])
        return max_time < delta
    return True


def parse_time(time_str):
    match = _time_regex.search(time_str)
    if not match:
        raise Exception("Could not parse suppress_time option: " + time_str)
    value = int(match.group(1))
    unit = match.group(2)
    return value * _time_seconds[unit]


def get_hash(msg):
    text = msg["title"] + msg["body"]
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# taken from: http://stackoverflow.com/questions/1158076/ddg#1160227
def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
                 dir_fd=None if os.supports_fd else dir_fd, **kwargs)


_time_regex = re.compile(r'([0-9]+) *([smhdwy])')
_time_seconds = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24, "w": 60*60*24*7,
                 "y": 60*60*24*365.25}
