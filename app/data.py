# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : data.py

def GetSeverArgs():
    server_args = {
        "all_scripts":False,

        "api_max_number":None,

        "custom_scripts":None,

        "default_scripts":False,

        "ip_segment":None,

        "output_file_name":None,

        "server":None,

        "show_all_scripts":False,

        "show_script_info":None,

        "spider_init_url":None,

        "target_file":None,

        "url":None,

        "zoomeye":None,

        "task_id":None,

        "update_script_info":False,

        "task_name":None,

        "zoomeye_search_type":None
    }
    return server_args

class TASKTYPE:
    URL = 0
    IPS = 1
    API = 2
    SPIDER = 3
    FILE = 4

class STATUS:
    WAIT = 'Waiting'
    RUN = 'Running'
    FINISH = 'Finish'
    FAIL = 'Failed'
    CLOSE = 'Close'