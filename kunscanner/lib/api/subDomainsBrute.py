# -*- coding: utf-8 -*-
# @Time   : 2018/5/29 下午5:32
# @author : Xmchx
# @File   : subDomainsBrute.py

import os
import IPy
from kunscanner.lib.core.data import args
from kunscanner.lib.core.exception import ArgsException

class SubDomainsBruteApi():
    def __init__(self):
        self.file_path = args.subdomain
        self.raw_data = ''
        self.result_list = []

    def Run(self):
        self.LoadTargetFile()
        self.LoadTarget()
        return self.result_list

    def LoadTargetFile(self):
        if os.path.exists(self.file_path) == False:
            raise ArgsException('The input subDomainBrute result file does not exist')
        try:
            f = open(self.file_path)
            self.raw_data = f.readlines()
        except Exception,e:
            raise ArgsException('Open subDomainBrute result file fail. exception:'+repr(e))

    def LoadTarget(self):
        target_list = []
        ip_list = []
        for line in self.raw_data:
            line = line.strip()
            data = line.split('\t')
            target_list.append(data[0].strip())
            ip = data[1].split(',')
            for each in ip:
                each = each.strip()
                ip_data = each.split('.')
                ip_data[-1] = '0'
                new_ip = '.'.join(ip_data)+'/24'
                if new_ip not in ip_list:
                    ip_list.append(new_ip)
        for ip in ip_list:
            ips = IPy.IP(ip)
            for i in ips:
                target_list.append(str(i))
        self.result_list = list(set(target_list))