# -*- coding: utf-8 -*-
# @Time   : 2018/4/30 下午12:09
# @author : Xmchx
# @File   : ceye.py


import requests
import json
from kunscanner.lib.core.data import conf

def CeyeApi(filter, query_type = 'dns'):
    url = 'http://api.ceye.io/v1/records?token='+conf.CEYE_TOKEN+'&type='+query_type+'&filter='+filter
    try:
        res = requests.get(url)
    except Exception,e:
        return False
    result = json.loads(res.text)['data']
    if len(result) == 0:
        return False
    else:
        return result
