from threading import Lock
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwds):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)

with managed_resource(timeout=3600) as resource:
    # Resource is released at the end of this block,
    # even if code in the block raises an exception

class ThreadSafeDict:
    def __init__(self):
        self._lock = Lock()
        self._dict = dict()

    def __call__(self, *args, **kwargs):
        try:
            yield self._dict


class Dispatcher:
    def __init__(self, input_queue, ):
    def __call__(self, *args, **kwargs):
