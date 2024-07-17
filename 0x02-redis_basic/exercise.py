#!/usr/bin/env python3
""" define Cashe class """
from functools import wraps
import redis
from typing import Any, Callable, Union, Optional
from uuid import uuid4


def count_calls(method: Callable) -> Callable:
    """Count calls decorator."""
    @wraps(method)
    def wrapper(self, *args, **kargs) -> Any:
        """ Implements counting functionality."""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs of a function."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs_key = "{}:inputs".format(method.__qualname__)
        outputs_key = "{}:outputs".format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(inputs_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(outputs_key, result)
        return result
    return wrapper


def replay(fn: Callable) -> None:
    """Display the history of calls."""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return

    inputs_key = '{}:inputs'.format(fn.__qualname__)
    outputs_key = '{}:outputs'.format(fn.__qualname__)

    call_counts = 0
    if redis_store.exists(fn.__qualname__) != 0:
        call_counts = int(redis_store.get(fn.__qualname__))

    print('{} was called {} times:'.format(fn.__qualname__, call_counts))
    inputs = redis_store.lrange(inputs_key, 0, -1)
    outputs = redis_store.lrange(outputs_key, 0, -1)
    for input_bytes, output_bytes in zip(inputs, outputs):

        input_str = input_bytes.decode('utf-8')
        output_str = output_bytes.decode('utf-8')
        print('{}(*{}) -> {}'.format(
            fn.__qualname__,
            input_str,
            output_str
        ))


class Cache:
    def __init__(self):
        """Constructor."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis."""
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """Get data from Redis."""
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Get string from Redis."""
        data = self._redis.get(key)
        return data.decode('utf-8')

    def get_int(self, key: str) -> int:
        """Get integer from Redis."""
        data = self._redis.get(key)
        return int(data)
