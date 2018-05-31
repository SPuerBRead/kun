# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : data.py

def GetSeverArgs():
    server_args = {
        "all_scripts":False,

        "max_number":None,

        "custom_scripts":None,

        "ip_segment":None,

        "output_file_name":None,

        "custom_scripts_info":False,

        "all_scripts_info":None,

        "spider_init_url":None,

        "target_file":None,

        "url":None,

        "zoomeye":None,

        "baidu":None,

        "task_id":None,

        "update_script_info":False,

        "task_name":None,

        "zoomeye_search_type":None,

        "subdomain":None,

        "custom_scripts_info":None,

        "search_script":None
    }
    return server_args


class TASKTYPE:
    URL = 0
    IPS = 1
    API = 2
    SPIDER = 3
    FILE = 4

class APINAME:
    ZOOMEYE = 'zoomeye'
    BAIDU = 'baidu'
    SUBDOMAIN = 'subDomainsBrute'

class STATUS:
    WAIT = 'Waiting'
    RUN = 'Running'
    FINISH = 'Finish'
    FAIL = 'Failed'
    CLOSE = 'Close'