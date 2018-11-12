from django.core.cache import cache


class NodeStatusCacheMgr(object):
    def __init__(self):
        pass

    def set_node_status(self, id, status):
        key = "ssrmgmt_node_status_" + str(id)
        if status:
            val = 'online'
        else:
            val = 'offline'
        cache.set(key, val, 80)

    def get_node_status(self, id):
        key = "ssrmgmt_node_status_" + str(id)
        if key in cache:
            return cache.get(key)
        else:
            return 'offline'

    def set_port_ips(self, port, ips: list):
        key = "ssrmgmt_port_status_" + str(port)
        cache.set(key, ips, 80)

    def get_port_ips(self, port):
        key = "ssrmgmt_port_status_" + str(port)
        if key in cache:
            return cache.get(key)
        else:
            return []
