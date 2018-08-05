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
            '-u': dct['-u'],
            '-p': dct['-p'],
            '-k': dct['-k'],
            '-m': dct['-m'],
            '-O': dct['-O'],
            '-G': dct['-G'],
            '-o': dct['-o'],
            '-s': dct['-s'],
            '-S': dct['-S'],
            '-t': dct['-t'],
            '-f': dct['-f'],
        }
        add_cmd = "cd /usr/local/shadowsocksr && python /usr/local/shadowsocksr/mujson_mgr.py -a"
        for k, v in params.items():
            add_cmd += " "
            add_cmd += k
            add_cmd += " "
            # 如果v是空字符串就赋值为""占位
            v = r'""' if v == "" else v
            add_cmd += str(v)

        res = os.popen(add_cmd)
        return res

"""cd /usr/local/shadowsocksr && python /usr/local/shadowsocksr/mujson_mgr.py -a
 -t 50 -f  -o tls1.2_ticket_auth_compatible -u fsasfa -S 0 -s 0 -G 5 -O auth_aes128_md5_compatible -m aes-128-ctr -k gasgdag -p 7883"""

"""python /usr/local/shadowsocksr/mujson_mgr.py -a
 -u fasfa -p 7777 -k 12345 -m aes-128-ctr -O auth_sha1_v4_compatible -G ""
  -o tls1.2_ticket_auth_compatible -s 0 -S 0 -t 100 -f "" """
