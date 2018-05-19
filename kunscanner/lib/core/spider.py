# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午10:02
# @author : Xmchx
# @File   : spider.py

import sys
import Queue
import re
import threading
import urlparse
import tldextract
import requests

from common import GetSystemType
from data import args, conf, path
from enums import EXCEPYION_POSITION, MESSAGE_LEVEL, SPIDER_TYPE, SYSTEM_TYPE, SCANNER_MODE
from exception import RequestsException
from kunscanner.lib.parse.cmdline import CmdLineParser
from log import SetLogger
from argsparse import SetOptions
from output import OutPutPadding,InfoOutPut2Console
from kunscanner.lib.utils.utils import GetHeader,LoadDict

from kunscanner.lib.core import SetArgs, SetConfig, SetPath


class DomainSpider():
    def __init__(self, scanner_mode, scan_args):
        GetSystemType()
        if conf.SYSTEM_TYPE == SYSTEM_TYPE.WINDOWS:
            self.InitSetting(scanner_mode, scan_args)
        self.spider_type = int(conf.SPIDER_TYPE)
        self.spider_status = False
        self.spider_queue = Queue.Queue()
        if self.spider_type == int(SPIDER_TYPE.DEPTH_SPIDER):
            self.domain = args.spider_init_url
            self.max_depth = conf.SPIDER_DEPTH
            self.depth = 1
        elif self.spider_type == int(SPIDER_TYPE.NUMBER_SPIDER):
            if args.spider_init_url.startswith('http://'):
                self.domain = args.spider_init_url
            else:
                self.domain = 'http://'+args.spider_init_url
            if args.max_number:
                self.max_number = int(args.max_number)
            else:
                self.max_number = int(conf.SPIDER_NUMBER)
            if self.max_number > 60000:
                self.max_number = 60000
            self.spider_queue_number = 1
            self.spider_all_number = 1
        elif self.spider_type == 3:
            pass
        self.threads = int(conf.SPIDER_THREADS)
        self.ignore_domains = LoadDict(path.DICT_PATH+conf.SPIDER_IGNORE_DOMAIN_FILE)
        self.domain_list = []


    def InitSetting(self, scanner_mode, scan_args):
        SetLogger()
        SetPath()
        SetConfig()
        if scanner_mode == SCANNER_MODE.CONSOLE:
            SetArgs(scanner_mode, CmdLineParser())
        else:
            SetArgs(scanner_mode, scan_args)
        SetOptions()

    def RunSpider(self, domain_queue, spider_info):
        msg = OutPutPadding('The spider started to run', MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        self.spider_info = spider_info
        self.domain_queue = domain_queue
        self.domain_queue.put(self.domain)
        self.spider_queue.put(self.domain)
        if self.spider_type == int(SPIDER_TYPE.DEPTH_SPIDER):
            pass
        if self.spider_type == int(SPIDER_TYPE.NUMBER_SPIDER):
            self.lock = threading.Lock()
            self.spider_status = True
            self.spider_info['spider_status'] = self.spider_status
            self.GetEnoughDomian()
            thread_list = []
            for i in range(0, self.threads):
                t = threading.Thread(target=self.MaxNumberSpider, args=(i,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
        msg = OutPutPadding('The spider is over', MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        msg = OutPutPadding('The number of targets found by the spider: {0}'.format(str(self.spider_all_number)),
                            MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        self.spider_info['spider_status'] = False

    def GetEnoughDomian(self):
        while self.spider_queue.qsize() < self.threads:
            try:
                domain = self.spider_queue.get(timeout=int(conf.QUEUE_TIMEOUT))
            except:
                break
            self.spider_queue_number -= 1
            self.spider_info['spider_queue_size'] = self.spider_queue_number
            header = GetHeader()
            try:
                req = requests.get(domain, headers=header, timeout=int(conf.SPIDER_REQUESTS_TIMEOUT))
            except Exception, e:
                RequestsException(e, EXCEPYION_POSITION.SPIDER, MESSAGE_LEVEL.WARNING_LEVEL, domain)
                continue
            domains = re.findall(re.compile(r'href\s*=\s*"(http://.*?|https://.*?)"'), req.text)
            self.AddToQueue(domains)

    def MaxNumberSpider(self, thread_id):
        while True:
            if self.spider_all_number <= self.max_number and self.spider_status == True:
                try:
                    domain = self.spider_queue.get(timeout=int(conf.QUEUE_TIMEOUT))
                    self.lock.acquire()
                    self.spider_queue_number -= 1
                    self.spider_info['spider_queue_size'] = self.spider_queue_number
                    self.lock.release()
                except Exception:
                    self.StopSpiderThread()
                    break
                try:
                    req = requests.get(domain, timeout=int(conf.SPIDER_REQUESTS_TIMEOUT))
                except Exception, e:
                    RequestsException(e, EXCEPYION_POSITION.SPIDER, MESSAGE_LEVEL.WARNING_LEVEL, domain)
                    continue
                domains = re.findall(re.compile(r'href\s*=\s*"(http://.*?|https://.*?)"'), req.text)
                self.AddToQueue(domains)
            else:
                self.StopSpiderThread()
                break

    def MaxDepthSpider(self):
        pass


    def AddToQueue(self, domains):
        for domain in domains:
            if isinstance(domain, unicode):
                try:
                    domain = domain.encode(sys.stdout.encoding)
                except:
                    domain = domain
            else:
                domain = domain
            try:
                domain_netloc = urlparse.urlparse(domain).netloc
            except:
                continue
            if self.DuplicateCheck(domain_netloc) == False or self.IgnoreCheck(domain_netloc) == False:
                continue
            self.domain_queue.put(domain)
            self.spider_queue.put(domain)
            self.lock.acquire()
            self.spider_all_number += 1
            self.spider_queue_number += 1
            self.spider_info['spider_queue_size'] = self.spider_queue_number
            self.spider_info['domain_queue_sise'] = self.spider_all_number
            self.domain_list.append(domain_netloc)
            self.lock.release()

    def DuplicateCheck(self, domain):
        if domain not in self.domain_list:
            return True
        else:
            return False

    def IgnoreCheck(self, domain):
        val = tldextract.extract(domain)
        try:
            full_domain = "*.{0}.{1}".format(val.domain, val.suffix)
        except:
            return False
        if domain in self.ignore_domains or full_domain in self.ignore_domains:
            return False
        else:
            return True


    def StopSpiderThread(self):
        self.lock.acquire()
        self.spider_status = False
        self.lock.release()
