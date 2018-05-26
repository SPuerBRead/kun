# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午9:41
# @author : Xmchx
# @File   : zoomeye.py

import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from kunscanner.lib.core.data import conf, args
from kunscanner.lib.core.enums import API_LOGIN_TYPE, EXCEPYION_POSITION, MESSAGE_LEVEL
from kunscanner.lib.core.exception import APIException, RequestsException
from kunscanner.lib.core.output import OutPutPadding,InfoOutPut2Console

if args.use_database == True:
    from kunscanner.lib.core.database import SaveWarningToDatabase

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ZoomeyeApi():
    def __init__(self):

        if conf.ZOOMEYE_USERNAME != 'none' and conf.ZOOMEYE_PASSWORD != 'none':
            self.login_type = API_LOGIN_TYPE.PASSWORD
            self.username = conf.ZOOMEYE_USERNAME
            self.password = conf.ZOOMEYE_PASSWORD
        elif conf.ZOOMEYE_ACCESS_TOKEN != 'none':
            self.login_type = API_LOGIN_TYPE.ACCESS_TOKEN
            self.access_token = conf.ZOOMEYE_ACCESS_TOKEN
        if args.max_number != None:
            self.max_number = int(args.max_number)
        else:
            self.max_number = int(conf.ZOOMEYE_MAX_NUMBER)
        if args.zoomeye_search_type:
            self.find_type = args.zoomeye_search_type
        else:
            self.find_type = conf.ZOOMEYE_SEARCH_TYPE
        self.keyword = args.zoomeye
        self.result_list = []

    def Run(self):
        if self.login_type == API_LOGIN_TYPE.PASSWORD:
            self.Login()
        self.header = {'Authorization': 'JWT %s' % self.access_token}
        self.ShowResourcesInfo()
        if self.find_type == 'host':
            self.HostSearch()
        elif self.find_type == 'web':
            self.WebSearch()
        else:
            raise APIException('Setting ZOOMEYE_FIND_TYPE item in the configuration file is wrong (host or web)')
        if len(self.result_list) == 0:
            message = 'Failed to find the appropriate target by calling the API, trying to change the keyword or modify ' \
                      'the ZOOMEYE_SEARCH_TYPE (host or web) in the configuration file (ZoomEye API References: ' \
                      'https://www.zoomeye.org/api)'
            msg = OutPutPadding(message, MESSAGE_LEVEL.WARNING_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.WARNING_LEVEL)
            SaveWarningToDatabase(message)
        return self.result_list

    def Login(self):
        get_token_url = 'https://api.zoomeye.org/user/login'
        user_info = {"username": self.username, "password": self.password}
        try:
            response = requests.post(get_token_url, data=json.dumps(user_info), verify=False)
        except Exception, e:
            raise APIException('Zoomeye login error! Error message:'+repr(e))
        if response.status_code != 200:
            raise APIException('Zoomeye login error: ' + json.loads(response.text)['message'])
        self.access_token = eval(response.text)['access_token']

    def ShowResourcesInfo(self):
        user_info_url = 'https://api.zoomeye.org/resources-info'
        try:
            response = requests.get(user_info_url, headers=self.header, verify=False)
        except Exception, e:
            RequestsException(e, EXCEPYION_POSITION.API, MESSAGE_LEVEL.WARNING_LEVEL, None)
            return
        message = 'API resources limit: {0}'
        msg = OutPutPadding(message.format(json.loads(response.text)['resources']['search']), MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)

    def HostSearch(self):
        error_time = 0
        page = 1
        host_search_url = "https://api.zoomeye.org/host/search?query={0}&page={1}"
        while len(self.result_list) < self.max_number:
            try:
                response = requests.get(host_search_url.format(self.keyword, str(page)), headers=self.header,
                                        verify=False, timeout=10)
            except Exception, e:
                RequestsException(e, EXCEPYION_POSITION.API, MESSAGE_LEVEL.ERROR_LEVEL, None)
                if error_time < 5:
                    error_time += 1
                    continue
                else:
                    break
            if response.status_code != 200:
                break
            data = json.loads(response.text)
            if len(data['matches']) == 0:
                break
            for each in data['matches']:
                target = each['ip'] + ':' + str(each['portinfo']['port'])
                self.result_list.append(target)
            self.OutPutStatus(str(len(self.result_list)))
            page += 1

    def WebSearch(self):
        error_time = 0
        page = 1
        web_search_url = "https://api.zoomeye.org/web/search?query={0}&page={1}"
        while len(self.result_list) < self.max_number:
            try:
                response = requests.get(web_search_url.format(self.keyword, str(page)), headers=self.header,
                                        verify=False, timeout=10)
            except Exception, e:
                RequestsException(e, EXCEPYION_POSITION.API, MESSAGE_LEVEL.ERROR_LEVEL, None)
                if error_time < 5:
                    error_time += 1
                    continue
                else:
                    break
            if response.status_code != 200:
                break
            data = json.loads(response.text)
            if len(data['matches']) == 0:
                break
            for each in data['matches']:
                target = each['site']
                self.result_list.append(target)
            self.OutPutStatus(str(len(self.result_list)))
            page += 1

    def OutPutStatus(self, number):
        msg = 'The number of targets currently available from the API: {0}'
        InfoOutPut2Console(msg.format(number), MESSAGE_LEVEL.STATUS_LEVEL)