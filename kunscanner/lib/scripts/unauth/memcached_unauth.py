# -*- coding: utf-8 -*-
# @Time   : 2018/4/29 上午11:21
# @author : Xmchx
# @File   : memcached_unauth.py


import socket
import re
from collections import OrderedDict
from kunscanner.lib.utils.utils import GetNetloc, DomainToIP, DelPort
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "memcached_unauth"
    poc_info['info'] = "memcached unauthorized access vulnerability"
    poc_info['title'] = u"Memcached未授权访问"
    poc_info['author'] = "i@cdxy.me"
    poc_info['time'] = "2018.04.29"
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
        port = int(ip.split(':')[-1]) if ':' in ip else 11211
        ip = DelPort(ip)
        payload = '\x73\x74\x61\x74\x73\x0a'
        s = socket.socket()
        s.connect((ip, port))
        s.send(payload)
        recvdata = s.recv(2048)
        s.close()
        if recvdata and 'STAT version' in recvdata:
            result['success'] = True
            result['message']  = 'version:' + ''.join(re.findall(r'version\s(.*?)\s', recvdata))
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))