# -*- coding: utf-8 -*-
# @Time   : 2018/5/26 上午11:51
# @author : Xmchx
# @File   : baidu.py

import socket
import re
import requests
import Queue
import threading
from kunscanner.lib.core.exception import APIException
from kunscanner.lib.core.data import conf, args
from kunscanner.lib.utils.utils import GetNetloc
from kunscanner.lib.core.output import OutPutPadding,InfoOutPut2Console
from kunscanner.lib.core.enums import MESSAGE_LEVEL

class BaiduApi():
    def __init__(self):
        if args.max_number != None:
            self.max_number = int(args.max_number)
        else:
            self.max_number = int(conf.BAIDU_MAX_NUMBER)
        self.keyword = args.baidu
        self.search_url = 'http://www.baidu.com/s?wd={0}&rn=50&pn={1}'
        self.regex_url = r'<div class="result c-container.*?".*?<h3 class=".*?"><a.*?href = "(.*?)".*?target="_blank"'
        self.domain_list = []
        self.result_list = []
        self.is_run = False
        self.raw_queue = Queue.Queue()
        self.lock = threading.Lock()
        socket.setdefaulttimeout(3)

    def Run(self):
        if self.Connect() == False:
            raise APIException('Unable to connect to http://www.baidu.com/')
        thread_list = []
        t = threading.Thread(target= self.GetData)
        t.start()
        thread_list.append(t)
        for thread_id in range(20):
            t = threading.Thread(target=self.GetRealURL)
            t.start()
            thread_list.append(t)
        for i in thread_list:
            i.join()
        message = 'Get the target from Baidu ended，Number of target:'+str(len(self.result_list))
        msg = OutPutPadding(message,
                            MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)
        return self.result_list

    def Connect(self):
        try:
            requests.get('http://www.baidu.com/',timeout = 10)
        except:
            return False
        return True

    def GetData(self):
        self.is_run = True
        page = 0
        fail_time = 0
        while len(self.result_list) < self.max_number:
            if page < 50:
                target = self.search_url.format(self.keyword, str(page*50))
                try:
                    req = requests.get(target,timeout = 3)
                    result = re.findall(re.compile(self.regex_url,re.S),req.text)
                    for each in result:
                        if each:
                            self.raw_queue.put(each.strip())
                    page += 1
                except:
                    if fail_time < 5:
                        fail_time += 1
                        continue
                    else:
                        break
            else:
                break
        self.is_run = False
        message = 'Crawl the Baidu link ends and the link is being parsed'
        msg = OutPutPadding(message,
                            MESSAGE_LEVEL.INFO_LEVEL)
        InfoOutPut2Console(msg, MESSAGE_LEVEL.INFO_LEVEL)

    def GetRealURL(self):
        while True:
            if self.raw_queue.qsize() <= 0 and self.is_run == False:
                break
            try:
                each = self.raw_queue.get(timeout=1)
                req = requests.get(each,timeout = 3)
                domain = GetNetloc(req.url, True)
                self.lock.acquire()
                if domain not in self.domain_list:
                    self.result_list.append(req.url)
                    self.domain_list.append(domain)
                self.OutPutStatus(str(len(self.result_list)), str(self.raw_queue.qsize()))
                self.lock.release()
            except Exception,e:
                pass



    def OutPutStatus(self, doamin_number,link_number):
        msg = 'The number of targets currently available from the API: {0}，Currently getting web links:{1}'
        InfoOutPut2Console(msg.format(doamin_number,link_number), MESSAGE_LEVEL.STATUS_LEVEL)