# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : weakfile.py

import requests
from collections import OrderedDict
from kunscanner.lib.core.data import path
from kunscanner.lib.utils.utils import GetNetloc,LoadDict,CheckTargetAccess
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

dict_path = path.DICT_PATH + 'weak_file'

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "weakfile"
    poc_info['info'] = "weak file scan. backup file/.git/svn and others"
    poc_info['title'] = u'敏感文件测试'
    poc_info['author'] = "Xmchx"
    poc_info['time'] = "2018.04.24"
    poc_info['type'] = 'info'
    poc_info['level'] = SCRIPT_LEVEL.LOW
    return poc_info


def Poc(url):
    init_url = url
    result = {}
    try:
        data = ''
        url = GetNetloc(url,True)
        if CheckTargetAccess(url):
            files = LoadDict(dict_path)
            for file in files:
                try:
                    file = file.strip()
                    res = requests.get(url[0:-1]+file, timeout=3)
                except:
                    continue
                if str(res.status_code).startswith('2'):
                    data = data+'\n'+file+': '+str(res.status_code)
            if data:
                result['weak_file'] = data
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))