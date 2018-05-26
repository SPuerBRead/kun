# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午8:05
# @author : Xmchx
# @File   : loader.py

from data import args,conf,path
from output import InfoOutPut2Console,OutPutPadding
from enums import TARGET_TYPE,MESSAGE_LEVEL,IPS_TYPE,API_TYPE,SCRIPT_TYPE,SCANNER_MODE,WORK_TYPE
from common import SysQuit
import multiprocessing
import urlparse
from exception import ArgsException,APIException
import IPy
import re
import os
from kunscanner.lib.api.zoomeye import ZoomeyeApi
from kunscanner.lib.api.baidu import BaiduApi
from spider import DomainSpider
import imp

class TargetLoader():

    def Loader(self):
        target_type_msg = 'Scan type: {0}'
        target_number_msg = 'Target number: {0}'
        api_type_msg = 'API type: {0}'
        if args.scan_type == TARGET_TYPE.SINGLE_URL:
            msg = OutPutPadding(target_type_msg.format('URL'), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.domain_list = []
            self.LoadSingleTarget()
            msg = OutPutPadding(target_number_msg.format(str(len(self.domain_list))), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        if args.scan_type == TARGET_TYPE.TARGET_FILE:
            msg = OutPutPadding(target_type_msg.format('FILE'), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.domain_list = []
            self.LoadFileTarget()
            msg = OutPutPadding(target_number_msg.format(str(len(self.domain_list))), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        if args.scan_type == TARGET_TYPE.IPS:
            msg = OutPutPadding(target_type_msg.format('IP'), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.domain_list = []
            self.LoadIpsTarget()
            msg = OutPutPadding(target_number_msg.format(str(len(self.domain_list))), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        if args.scan_type == TARGET_TYPE.SPIDER:
            self.domain_queue = multiprocessing.Queue()
            msg = OutPutPadding(target_type_msg.format('SPIDER'), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            spider_init_domain_msg = 'Spider init domain: {0}'
            msg = OutPutPadding(spider_init_domain_msg.format(args.spider_init_url), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.LoadSpiderTarget()
        if args.scan_type == TARGET_TYPE.API:
            self.domain_list = []
            msg = OutPutPadding(target_type_msg.format('API'), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            msg = OutPutPadding(api_type_msg.format(args.api_type), MESSAGE_LEVEL.INFO_LEVEL)
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.LoadApiTarget()

    def LoadSingleTarget(self):
        if self.CheckIp(args.url) or self.CheckDomain(args.url):
            self.domain_list.append(args.url)
        else:
            raise ArgsException('The specified target format is incorrect, please re-enter')

    def LoadIpsTarget(self):
        if '-' in args.ip_segment:
            self.StrToIp(IPS_TYPE.IPS)
        elif '/' in args.ip_segment:
            self.StrToIp(IPS_TYPE.SUBNETMASK)
        else:
            raise ArgsException('The entered IP address range is not valid')

    def LoadFileTarget(self):
        if os.path.exists(path.START_PATH + '/' + args.target_file) == False:
            raise ArgsException('The input scanned target file does not exist')
        with open(path.START_PATH + '/' + args.target_file) as f:
            data = f.readlines()
            for line in data:
                line = line.strip()
                if line:
                    if self.CheckIp(line) or self.CheckDomain(line):
                        self.domain_list.append(line.strip())

    def LoadApiTarget(self):
        if args.api_type == API_TYPE.ZOOMEYE:
            api = ZoomeyeApi()
        if args.api_type == API_TYPE.BAIDU:
            api = BaiduApi()
        try:
            self.domain_list = api.Run()
        except APIException:
            SysQuit()

    def LoadSpiderTarget(self):
        manager = multiprocessing.Manager()
        self.spider_info = manager.dict()
        self.spider_info['spider_status'] = False
        self.spider_info['domain_queue_sise'] = 0
        self.spider_info['spider_queue_size'] = 0
        spider_process = multiprocessing.Process(target=self.StartDomainSpider)
        spider_process.start()

    def StartDomainSpider(self):
        spider = DomainSpider(args.scanner_mode, args.scan_args,self.domain_queue, self.spider_info)
        spider.RunSpider()

    def StrToIp(self, ips_type):
        if ips_type == IPS_TYPE.IPS:
            ips = args.ip_segment.split('-')
            # 192.168.0.1-192.168.0.254
            if '.' in ips[1]:
                if self.CheckIp(ips[0]) == False or self.CheckIp(ips[1]) == False:
                    raise ArgsException('The entered IP address range is not valid')
                ip1, ip2 = ips[0].split('.'), ips[1].split('.')
                for i in range(4):
                    if ip1[i] == ip2[i]:
                        continue
                    if ip1[i] < ip2[i]:
                        break
                    if ip1[i] > ip2[i]:
                        raise ArgsException('The entered IP address range is not valid')
                ip_sum = self.Addr2Dec(ips[1]) - self.Addr2Dec(ips[0])
                if ip_sum > int(conf.MAX_IP_COUNT):
                    raise ArgsException(
                        'The number of IP exceeds the maximum limit, the maximum number is {0}'.format(
                            conf.MAX_IP_COUNT))
                self.domain_list.append(ips[0])
                start_ip, end_ip = ips[0], ips[1]
                while (start_ip != end_ip):
                    start_ip = self.GetNextIp(start_ip)
                    if start_ip != '':
                        self.domain_list.append(start_ip)
            else:
                # 192.168.0.1-254
                if self.CheckIp(ips[0]) == False:
                    raise ArgsException('The entered IP address range is not valid')
                ip1 = ips[0].split('.')
                if int(ips[1]) < 0 or int(ips[1]) > 255 or int(ip1[3]) > int(ips[1]):
                    raise ArgsException('The entered IP address range is not valid')
                str_ip = str(ip1[0]) + '.' + str(ip1[1]) + '.' + str(ip1[2]) + '.' + "{0}"
                for number in range(int(ip1[3]), int(ips[1]) + 1):
                    self.domain_list.append(str_ip.format(str(number)))
        elif ips_type == IPS_TYPE.SUBNETMASK:
            try:
                domain_tmp_list = IPy.IP(args.ip_segment)
            except Exception, e:
                raise ArgsException('The entered IP address range is not valid')
            for ip in domain_tmp_list:
                self.domain_list.append(str(ip))

    def GetNextIp(self, start_ip):
        bits = start_ip.split('.')
        i = len(bits) - 1
        while (i >= 0):
            n = int(bits[i])
            if n >= 255:
                bits[i] = '0'
                i -= 1
            else:
                n += 1
                bits[i] = str(n)
                break
        if i == -1:
            return ''
        ip = ''
        for j in range(len(bits)):
            if j == len(bits) - 1:
                ip += bits[j]
            else:
                ip += bits[j] + '.'
        return ip

    def CheckIp(self, ip):
        if not ip.startswith('http'):
            ip = 'http://'+ip
        up = urlparse.urlparse(ip)
        if up.netloc:
            if ':' in up.netloc:
                ip = up.netloc.split(':')[0]
            else:
                ip = up.netloc
        regex = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if regex.match(ip):
            return True
        else:
            return False

    def CheckDomain(self,domain):
        if not domain.startswith('http'):
            domain = 'http://'+domain
        up = urlparse.urlparse(domain)
        if up.netloc:
            if ':' in up.netloc:
                d = up.netloc.split(':')[0]
            else:
                d = up.netloc
        regex = re.compile(r'(?i)^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
        if regex.match(d):
            return True
        else:
            return False

    def Addr2Dec(self, addr):
        items = [int(x) for x in addr.split(".")]
        return sum([items[i] << [24, 16, 8, 0][i] for i in range(4)])


class ScriptLoader():

    def Loader(self):
        self.all_script_list = []
        self.script_object_list = []
        self.LoadAllScriptName()

        if args.script_type == SCRIPT_TYPE.ALL_SCRIPT:
            self.ShowScriptType('all scrips')
            self.LoadAllScripts()
        elif args.script_type == SCRIPT_TYPE.CUSTOM_SCRIPT:
            self.ShowScriptType('custom scrips')
            self.LoadCustomScripts()

    def ShowScriptType(self, script_type):
        if args.work_type == WORK_TYPE.SCAN:
            if args.scanner_mode == SCANNER_MODE.CONSOLE:
                script_type_msg = 'Script type: {0}'
                msg = OutPutPadding(script_type_msg.format(script_type), MESSAGE_LEVEL.INFO_LEVEL)
                InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)

    def LoadAllScriptName(self):
        for root, dirs, scripts in os.walk(path.SCRIPTS_PATH):
            for script in scripts:
                script_info = {}
                if '__init__' not in script and 'pyc' not in script and 'py' in script:
                    script_info['name'] = script.split('.')[0]
                    script_info['path'] = os.path.join(root, script)
                    self.all_script_list.append(script_info)

    def LoadDirectoryScriptname(self, directory_name):
        script_list = []
        if os.path.exists(path.SCRIPTS_PATH + '/' + directory_name) == False:
            raise ArgsException('No specified attack script directory ({0}) was found.'.format(directory_name))
        for root, dirs, scripts in os.walk(path.SCRIPTS_PATH + '/' + directory_name):
            for script in scripts:
                script_info = {}
                ext = script.split('.')[-1]
                if '__init__' not in script and ext == 'py':
                    script_info['name'] = script.split('.')[0]
                    script_info['path'] = root
                    script_list.append(script_info)
        return script_list

    def GetAllScriptDirectoryName(self):
        dirs_list = []
        tmp_dir_names = os.listdir(path.SCRIPTS_PATH)
        for d in tmp_dir_names:
            p = os.path.join(path.SCRIPTS_PATH, d)
            if os.path.isdir(p):
                dirs_list.append(p)
        dirs_list.append(path.SCRIPTS_PATH)
        return dirs_list

    def LoadAllScripts(self):
        for script in self.all_script_list:
            file, file_path, desc = imp.find_module(script['name'], self.GetAllScriptDirectoryName())
            script_object = imp.load_module(script['name'], file, file_path, desc)
            script_dict = {}
            script_dict['object'] = script_object
            script_dict['name'] = script['name']
            self.script_object_list.append(script_dict)


    def LoadCustomScripts(self):
        args_scripts = []
        if ',' in args.custom_scripts:
            args_scripts = args.custom_scripts.split(',')
        else:
            args_scripts.append(args.custom_scripts)
        dirs_list = self.GetAllScriptDirectoryName()
        for args_script in args_scripts:
            if '*' in args_script:
                script_list = self.LoadDirectoryScriptname(args_script.strip('*'))
                for script in script_list:
                    file, file_path, desc = imp.find_module(script['name'], [script['path']])
                    script_object = imp.load_module(script['name'], file, file_path, desc)
                    script_dict = {}
                    script_dict['object'] = script_object
                    script_dict['name'] = script['name']
                    self.script_object_list.append(script_dict)
            else:
                try:
                    file, file_path, desc = imp.find_module(args_script, dirs_list)
                except Exception, e:
                    raise ArgsException('Load script ({0}) fail'.format(args_script))
                if file == None:
                    raise ArgsException('The specified attack script ({0}) was not found.'.format(args_script))
                script_object = imp.load_module(args_script, file, file_path, desc)
                script_dict = {}
                script_dict['object'] = script_object
                script_dict['name'] = args_script
                self.script_object_list.append(script_dict)