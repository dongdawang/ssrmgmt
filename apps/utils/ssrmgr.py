import json
import os


class SsrMgr:
    def __int__(self):
        self.path = os.path.abspath(r'/usr/local/shadowsocksr/mudb.json')

    def band_record(self):
        """返回用户的流量使用情况
        :return: duct, key=username, value={u:'', d:''}
        """
        band_usage = {}
        info_lst = []
        print(__file__)
        with open(r'mudb.json', 'rb') as f:
            info_lst = json.load(f)
        info_lst = json.loads(info_lst)
        if info_lst is not None:
            if isinstance(info_lst, list):
                for user in info_lst:
                    name = user['user']
                    u = user['u']
                    d = user['d']
                    band_usage[name] = {
                        'upload': u,
                        'download': d,
                    }

        return band_usage

    def add_account(self, dct):
        params = {
            '-u': dct['user'],
            '-p': dct['port'],
            '-k': dct['password'],
            '-m': dct['method'],
            '-O': dct['protocol'],
            '-G': dct['protocol_param'],
            '-o': dct['obfs'],
            '-s': dct['limit_per_con'],
            '-S': dct['limit_per_user'],
            '-t': dct['transfer'],
            '-f': dct['forbid'],
        }
        add_cmd = "/usr/local/shadowsocksr/python -a"
        for k, v in params.items():
            add_cmd += " "
            add_cmd += k
            add_cmd += " "
            add_cmd += str(v)

        res = os.popen(add_cmd)
        return res