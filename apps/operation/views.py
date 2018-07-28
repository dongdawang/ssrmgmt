from random import randint

from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.views import View
from apps.utils.mixin import LoginRequireMixin
from .forms import CreateAccountForm
from goods.models import SsrAccount

from apps.utils.ssrmgr import SsrMgr


class CreateAccount(LoginRequireMixin, View):
    account = {
        'name': '',
        'port': '',
        'password': '',
        'method': ['aes-128-ctr', 'rc4', 'rc4-md5', 'rc4-md5-6', 'aes-192-ctr',
                   'aes-256-ctr', 'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb', 'aes-128-cfb8',
                   'aes-192-cfb8', 'aes-256-cfb8'],
        # [注意] 如果使用 auth_chain_* 系列协议，建议加密方式选择 none (该系列协议自带 RC4 加密)，混淆随意]
        'protocol': ['auth_aes128_md5', 'origin', 'auth_sha1_v4', 'auth_aes128_sha1', 'auth_chain_a',
                     'auth_chain_b'],
        'protocol_compatible': True,
        'obfs': ['tls1.2_ticket_auth', 'plain', 'http_simple', 'http_post', 'random_head', ],
        'obfs_compatible': True,
        'transfer_enable': ['50', '100', '150', '200'],
    }

    def get(self, request, ip):
        """返回创建账户的页面
        """
        self.account['ip'] = ip

        return render(request, 'operation/createaccount.html',
                      {'account': self.account, 'info': None})

    def post(self, request):
        caf = CreateAccountForm(request.POST)
        ip = request.POST.get("ip")
        self.account['ip'] = ip
        if caf.is_valid():
            username = request.POST.get("username", "")
            query = SsrAccount.objects.filter(account_name=username)
            if len(query) != 0:
                return render(request, 'operation/createaccount.html',
                              {'account': self.account, 'info': '用户名已存在'})
            else:
                rand_port = randint(6900, 7900)
                ports = SsrAccount.objects.values_list('port')
                protocol = request.POST.get('protocol', '')
                if request.POST.get('protocol_yn') == 'on':
                    protocol += '_compatible'
                obfs = request.POST.get('obfs', '')
                if request.POST.get('obfs_yn') == 'on':
                    obfs += '_compatible'
                if rand_port in ports:
                    rand_port = randint(6900, 7900)
                acout = {
                    '-u': username,
                    '-p': rand_port,
                    '-k': request.POST.get("password", ""),
                    '-m': request.POST.get("method", ""),
                    '-O': protocol,
                    '-G': 5,  # 每个端口同一时间能连接的设备数
                    '-o': obfs,
                    '-s': 0,
                    '-S': 0,
                    '-t': request.POST.get("transfer_enable", ""),
                    '-f': "",
                }
                # sgr = SsrMgr()
                # sgr.add_account(acout)
                ssr_account = SsrAccount()
                ssr_account.ip = ip
                ssr_account.user = request.user
                ssr_account.account_name = username
                ssr_account.port = rand_port
                ssr_account.save()

        else:
            return render(request, 'operation/createaccount.html',
                          {'account': self.account, 'info': '用户名或者密码不合法'})
        return redirect('/')
