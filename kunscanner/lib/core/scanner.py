# -*- coding: utf-8 -*-
# @Time   : 2018/3/25 上午1:28
# @author : Xmchx
# @File   : scanner.py

import sys
import Queue
import threading
import urlparse
from enums import TARGET_TYPE, MESSAGE_LEVEL,STATUS,SCRIPT_LEVEL
from data import args, conf
from output import OutPutPadding,InfoOutPut2Console,OutputFinalResults, WriteResultToFile
from exception import PocWarningException, PocErrorException
if args.use_database:
    from database import SaveResultToDatabase, SaveProgressToDatabase,SaveStatusToDatabase
from kunscanner.lib.core.common import SysQuit
from kunscanner.lib.utils.terminalsize import get_terminal_size

width , height = get_terminal_size()


class Scanner():
    def __init__(self, target_loader, script_loader):
        self.target_loader = target_loader
        self.script_loader = script_loader
        self.script_object_list = script_loader.script_object_list
        self.scanner_status = False
        self.lock = threading.Lock()
        self.thread_list = []
        self.scan_number = 0
        self.error_msg = "Warning in scanner! target: {0} poc: {1} msg: {2}"
        self.success_number = 0
        self.scan_result = []
        self.all_size = 0
        self.high_count = 0
        self.medium_count = 0
        self.low_count = 0
        self.spider_target_list = []

    def Run(self):
        if args.scan_type == TARGET_TYPE.SPIDER:
            self.domain_queue = self.target_loader.domain_queue
            self.spider_info = self.target_loader.spider_info
            self.scanner_status = True
            for thread_id in range(int(conf.SCANNER_THREAD)):
                t = threading.Thread(target=self.SpiderScanner, args=(thread_id,))
                t.start()
                self.thread_list.append(t)
            for t in self.thread_list:
                t.join()
        else:
            self.domain_list = self.target_loader.domain_list
            self.scan_queue = Queue.Queue()
            self.CompositeScanQueue()
            self.scanner_status = True
            for thread_id in range(int(conf.SCANNER_THREAD)):
                t = threading.Thread(target=self.CommonScanner, args=(thread_id,))
                t.start()
                self.thread_list.append(t)
            for t in self.thread_list:
                t.join()
        message = 'Attack success number: {0}'
        msg = OutPutPadding(message.format(str(self.success_number)), MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        OutputFinalResults(self.scan_result)
        WriteResultToFile(self.scan_result)
        if args.use_database:
            data = {}
            data['high_count'] = self.high_count
            data['medium_count'] = self.medium_count
            data['low_count'] = self.low_count
            data['result'] = self.scan_result
            SaveResultToDatabase(data)
            SaveProgressToDatabase('100')
            SaveStatusToDatabase(STATUS.FINISH)


    def SpiderScanner(self,thread_id):
        while True:
            if self.scanner_status == True:
                script_object_list = self.script_object_list
                info = {}
                try:
                    target = self.domain_queue.get(timeout=int(conf.QUEUE_TIMEOUT))
                except Exception:
                    if self.spider_info['spider_status'] == False and self.scan_number >= \
                            self.spider_info['domain_queue_sise']:
                        self.lock.acquire()
                        self.scanner_status = False
                        self.lock.release()
                        break
                    else:
                        continue
                self.lock.acquire()
                self.spider_target_list.append(target)
                self.lock.release()
                for script in script_object_list:
                    self.lock.acquire()
                    self.scan_number = self.scan_number + 1
                    self.lock.release()
                    self.OutPutStatus(target, script['name'],thread_id)
                    try:
                        result = script['object'].Poc(target)
                    except PocWarningException:
                        continue
                    except PocErrorException:
                        SysQuit(1)
                    info['target'] = target
                    info['script_name'] = script['name']
                    info['object'] = script['object']
                    self.ScanResultHandler(info, result)
            else:
                break

    def CommonScanner(self, thread_id):
        while True:
            if self.scan_queue.qsize() > 0 or self.scanner_status == True:
                try:
                    info = self.scan_queue.get(timeout=int(conf.QUEUE_TIMEOUT))
                except Exception:
                    self.lock.acquire()
                    self.scanner_status = False
                    self.lock.release()
                    break
                self.lock.acquire()
                self.scan_number = self.scan_number + 1
                self.lock.release()
                self.OutPutStatus(info['target'], info['script_name'],thread_id)
                if self.scan_number % 20 == 0:
                    self.UpdateScanProgress()
                try:
                    result = info['object'].Poc(info['target'])
                except PocWarningException:
                    continue
                except PocErrorException:
                    SysQuit(1)
                self.ScanResultHandler(info, result)
            else:
                self.lock.acquire()
                self.scanner_status = False
                self.lock.release()
                sys.exit()

    def CompositeScanQueue(self):
        for target in self.domain_list:
            for script in self.script_object_list:
                self.scan_info_dict = {}
                self.scan_info_dict['target'] = target
                self.scan_info_dict['script_name'] = script['name']
                self.scan_info_dict['object'] = script['object']
                self.scan_queue.put(self.scan_info_dict)
        self.all_size = self.scan_queue.qsize()

    def UpdateScanProgress(self):
        self.lock.acquire()
        SaveProgressToDatabase("%.2f" %(float(self.scan_number) / float(self.all_size) * 100))
        self.lock.release()


    def OutPutStatus(self, target, script,thread):
        if target.startswith('http'):
            domain_parse = urlparse.urlparse(target)
            domain = domain_parse.scheme+'://'+domain_parse.netloc+'/'
        else:
            domain = target
        if len(domain) > int(width/2):
            domain = domain[:int(width/2)]
        msg = 'TARGET: ' + domain + ' SCRIPT: ' + script + ' THREAD_ID: '+str(thread)+' FINISH: ' + str(self.scan_number)
        self.lock.acquire()
        InfoOutPut2Console(msg, MESSAGE_LEVEL.STATUS_LEVEL)
        self.lock.release()

    def OutPutSuccessInfo(self,data):
        if data['type'] == 'attack':
            if data['result']['message'] == '':
                msg = 'FOUND! target: ' + data['target'] + ' script: ' + data['script']
            else:
                msg = 'FOUND! target: ' + data['target'] + ' script: ' + data['script'] + ' message: ' + \
                      data['result']['message']
        # if data['type'] == 'info':
        #     for key,value in data['result'].items():
        #         if value:
        #             msg_list.append('[+] '+'target: ' + data['target'] + ' script: ' + data['script']+' '
        #                             +str(key)+': '+str(value))
        #         else:
        #             msg_list.append('[+] '+'target: ' + data['target'] + ' script: ' + data['script']+' '
        #                             +str(key)+': '+'unknown')
            msg = OutPutPadding(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.lock.acquire()
            InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
            self.lock.release()

    def StatisticalSuccessNumber(self):
        self.lock.acquire()
        self.success_number += 1
        self.lock.release()


    def ResultFormat(self,data):
        is_exist = False
        result_dict_tmp = {}
        self.lock.acquire()
        for each in self.scan_result:
            if each['target'] == data['target']:
                single_script_result_dict = {}
                if data['type'] == 'attack':
                    single_script_result_dict['script_name'] = data['script']
                    single_script_result_dict['script_type'] = 'attack'
                    single_script_result_dict['message'] = data['result']['message']
                elif data['type'] == 'info':
                    single_script_result_dict['script_name'] = data['script']
                    single_script_result_dict['script_type'] = 'info'
                    single_script_result_dict['items'] = data['result']
                each['result'].append(single_script_result_dict)
                is_exist = True
                break
        self.lock.release()
        if is_exist == False:
            result_dict_tmp['target'] = data['target']
            result_dict_tmp['result'] = []
            single_script_result_dict = {}
            if data['type'] == 'attack':
                single_script_result_dict['script_name'] = data['script']
                single_script_result_dict['script_type'] = 'attack'
                single_script_result_dict['message'] = data['result']['message']
            elif data['type'] == 'info':
                single_script_result_dict['script_name'] = data['script']
                single_script_result_dict['script_type'] = 'info'
                single_script_result_dict['items'] = data['result']
            result_dict_tmp['result'].append(single_script_result_dict)
            self.scan_result.append(result_dict_tmp)




    def ScanResultHandler(self, info, result):
        data = {}
        if info['target'].startswith('http'):
            target = info['target']
        else:
            target = 'http://'+info['target']
        domain_parse = urlparse.urlparse(target)
        domain = domain_parse.netloc
        if info['object'].Info()['type'] == 'info' and len(result):
            data['target'] = domain
            data['result'] = result
            data['script'] = info['script_name']
            data['type'] = 'info'
        elif info['object'].Info()['type'] == 'attack':
            if result['success'] == True:
                self.StatisticalSuccessNumber()
                data['target'] = domain
                data['result'] = result
                data['script'] = info['script_name']
                data['type'] = 'attack'
                data['level'] = info['object'].Info()['level']
                self.Statistics(data['level'])
            else:
                return
        else:
            return
        self.OutPutSuccessInfo(data)
        self.ResultFormat(data)


    def Statistics(self,level):
        if level == SCRIPT_LEVEL.HIGH:
            self.lock.acquire()
            self.high_count += 1
            self.lock.release()
        elif level == SCRIPT_LEVEL.MEDIUM:
            self.lock.acquire()
            self.medium_count += 1
            self.lock.release()
        elif level == SCRIPT_LEVEL.LOW:
            self.lock.acquire()
            self.low_count += 1
            self.lock.release()