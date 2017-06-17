import time

from contextlib import contextmanager
from django.core.cache import cache

from retribution.core.exceptions import LockAquisitionError


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


@contextmanager
def lock(key, retry_interval=1, retry=0, ttl=10, release_on_exit=False):
    """ Context manager to lock shared resources. Handy to prevent race conditions.
        key = memcached key for shared resource
        retry_interval = interval in seconds to retry getting lock
        retry = retry this many time before raising error
        ttl = key expiry time(in s), to prevent key locking up indefinitely
        release_on_exit = if True, lock will be deleted before returning
    """
    if cache.add(key, True, ttl):
        yield
        if release_on_exit:
            cache.delete(key)
        return
    else:
        for retry_count in range(0, retry):
            time.sleep(retry_interval)
            if cache.add(key, True, ttl):
                yield
                if release_on_exit:
                    cache.delete(key)
                return
        raise LockAquisitionError()
