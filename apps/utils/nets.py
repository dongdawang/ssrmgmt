import socket

from django.core.cache import cache


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_host_ip_cache():
    key = 'host_ip'
    if key in cache:
        host_ip = cache.get(key)
    else:
        host_ip = get_host_ip()
        cache.set(key, host_ip, 60*60*60*24)
    return host_ip
