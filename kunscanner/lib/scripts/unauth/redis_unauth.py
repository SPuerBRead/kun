# -*- coding: utf-8 -*-
# @Time   : 2018/3/25 上午1:41
# @author : Xmchx
# @File   : redis_unauth.py


import socket
from collections import OrderedDict

from kunscanner.lib.utils.utils import DelPort,GetNetloc,DomainToIP
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL


def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "redis_unauth"
    poc_info['info'] = "redis unauthorized access vulnerability"
    poc_info['title'] = u'Redis未授权访问'
    poc_info['author'] = "i@cdxy.me"
    poc_info['time'] = "2018.03.03"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.MEDIUM
    return poc_info



def Poc(url):
    init_url = url
    result = {}
    result['success'] = False
    result['message'] = ''

    try:
        socket.setdefaulttimeout(3)
        url = GetNetloc(url)
        ip = DomainToIP(url)
        if ip == None:
            return result
        payload = '\x2a\x31\x0d\x0a\x24\x34\x0d\x0a\x69\x6e\x66\x6f\x0d\x0a'
        port = int(ip.split(':')[-1]) if ':' in ip else 6379
        ip = DelPort(ip)
        s = socket.socket()
        s.connect((ip, port))
        s.send(payload)
        recvdata = s.recv(1024)
        s.close()
        if recvdata and 'redis_version' in recvdata:
            result['success'] = True
        return result
    except Exception,e:
        raise PocWarningException(init_url, Info()['name'], repr(e))
