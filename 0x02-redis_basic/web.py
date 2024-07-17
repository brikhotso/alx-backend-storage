#!/usr/bin/env python3
"""
    Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it
"""
import redis
import requests

redi = redis.Redis()

def get_page(url: str) -> str:
    """Fetch HTML content of URL, caches it, and tracks access count"""
    # Increment access count every time the function is called
    access_count_key = "count:{}".format(url)
    redi.incr(access_count_key)

    # Check for cached content
    cached_content_key = "cached:{}".format(url)
    cached_content = redi.get(cached_content_key)

    if cached_content:
        return cached_content.decode()

    # If not cached, fetch and cache the content
    response = requests.get(url)
    redi.setex(cached_content_key, 10, response.text)
    return response.text

if __name__ == "__main__":
    url = 'http://slowwly.robertomurray.co.uk'
    print(get_page(url))
    print(get_page(url))
