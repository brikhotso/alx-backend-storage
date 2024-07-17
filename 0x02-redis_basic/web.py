#!/usr/bin/env python3
"""
Defines a function `get_page`
"""
import redis
import requests
from datetime import datetime, timedelta


cache = redis.Redis()


def cache_decorator(func):
    """"""
    @wraps(func)
    def wrapper(url):
        """
        Use requests module to obtain
         HTML content of a particular URL
        """
        current_time = datetime.now()
        # Check if URL is in cache and not expired
        if url in cache and (current_time - cache[url]['time']).seconds < 10:
            cache[url]['count'] += 1
            return cache[url]['content']
        else:
            # Fetch new content, reset cache for URL
            content = func(url)
            cache[url] = {
                'content': content,
                'time': current_time,
                'count': 1
            }
            return content
    return wrapper

@cache_decorator
def get_page(url: str) -> str$:
    """returns HTML content of a particular URL """
    response = requests.get(url)
    return response.text
