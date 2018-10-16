import base64


def url_safe64(text):
    text = str(text, encoding='utf-8')
    text = text.replace(" ", "")
    text = text.replace("=", "")
    text = text.replace("+", "-")
    text = text.replace(r"/", "_")
    return text


class SS:
    """SS的相关信息"""
    def __init__(self, ss):
        txt = "{}:{}@{}:{}".format(ss.method, ss.passwd, ss.node.ip, ss.port)
        btxt = bytes(txt, encoding='utf-8')
        self.ssbase64 = url_safe64(base64.b64encode(btxt))

    @property
    def qrcode(self):
        return "https://makeai.cn/qr/?m=2&e=H&p=3&url={}".format(self.ssbase64)

    @property
    def url(self):
        return "ss://{}".format(self.ssbase64)


class SSR:
    """SSR的相关信息"""
    def __init__(self, ssr):
        protocol = ssr.protocol.replace("_compatible", "")
        obfs = ssr.obfs.replace("_compatible", "")
        pwdbase64 = url_safe64(base64.b64encode(bytes(ssr.passwd, encoding='utf8')))
        txt = "{}:{}:{}:{}:{}:{}".format(ssr.node.ip, ssr.port, protocol, ssr.method, obfs, pwdbase64)
        btxt = bytes(txt, encoding='utf8')
        self.ssrbase64 = url_safe64(base64.b64encode(btxt))

    @property
    def qrcode(self):
        return "https://makeai.cn/qr/?m=2&e=H&p=3&url={}".format(self.ssrbase64)

    @property
    def url(self):
        return "ssr://{}".format(self.ssrbase64)
