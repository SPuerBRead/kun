# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午2:31
# @author : Xmchx
# @File   : webapi.py

import os
import ConfigParser
from kunscanner.scanner import Main as RunScanner

'''
选中全部脚本扫描
all_scripts=False

api获取的最大数目
api_max_number=None

自定义加载扫描脚本
custom_scripts='unauth*'

使用默认的扫描脚本，还没开发完
default_scripts=False,

IP段类型的目标，可以接受{192.168.0.1-10，192.168.0.1-192.168.1.1.192.168.0.0/24}
ip_segment=None

扫描结果的输出文件名，可不填，为空时文件名为扫描结束时间
output_file_name=None

显示当前可用的所有插件信息
all_scripts_info=False

显示指定的插件信息
custom_scripts_info=None

从爬虫获取目标，值为爬虫的起始域名
spider_init_url=None

从文本文件加载目标
target_file=None

指定本次扫描的任务名，只在使用数据库作为存储是有效
task_name=None,

单独一个url的扫描
url='127.0.0.1',

使用zoomeye获取目标，值为zoomeye的搜索关键字
zoomeye=None
'''

def NewScan(args):
    '''
    example：
    args = {
        "all_scripts":False,
        "api_max_number":None,
        "custom_scripts":'unauth*',
        "default_scripts":False,
        "ip_segment":None,
        "output_file_name":None,
        "all_scripts_info":False,
        "custom_scripts_info":None,
        "spider_init_url":None,
        "target_file":None,
        "task_name":None,
        "url":'127.0.0.1',
        "zoomeye":None
    }
    '''
    RunScanner('web',args)


def ScriptsInfo():
    args = {

        "all_scripts":False,

        "max_number":None,

        "custom_scripts":None,

        "ip_segment":None,

        "output_file_name":None,

        "custom_scripts_info":None,

        "all_scripts_info":True,

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

        "search_script": None,

        "custom_scripts_info":None
    }
    return RunScanner('web',args)


def APIInfo():
    api_list = []
    api_path =  os.path.dirname(os.path.realpath(__file__))+'//lib//api//'
    for root, dirs, files in os.walk(api_path):
            for file in files:
                if '__init__' not in file and 'pyc' not in file and 'pyo' not in file and 'py' in file:
                    api_list.append(file.split('.')[0])
    return api_list

