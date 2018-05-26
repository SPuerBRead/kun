# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : task.py

from extensions import celery
from kunscanner.webapi import NewScan
from data import GetSeverArgs


@celery.task(bind=True)
def UrlScanTask(self,target,script,task_name):
    server_args = GetSeverArgs()
    server_args['url'] = target
    server_args['custom_scripts'] = script
    server_args['task_name'] = task_name
    server_args['task_id'] = self.request.id
    NewScan(server_args)


@celery.task(bind=True)
def IPSScanTask(self,target,script,task_name):
    server_args = GetSeverArgs()
    server_args['ip_segment'] = target
    server_args['custom_scripts'] = script
    server_args['task_name'] = task_name
    server_args['task_id'] = self.request.id
    NewScan(server_args)

@celery.task(bind=True)
def SpiderScanTask(self,target,script,task_name,number):
    server_args = GetSeverArgs()
    server_args['spider_init_url'] = target
    server_args['custom_scripts'] = script
    server_args['task_name'] = task_name
    server_args['task_id'] = self.request.id
    server_args['max_number'] = number
    NewScan(server_args)


@celery.task(bind=True)
def ApiScanTask(self,api_name,keyword,script,task_name,number,search_type):
    server_args = GetSeverArgs()
    if api_name == 'zoomeye':
        server_args['zoomeye'] = keyword
        server_args['custom_scripts'] = script
        server_args['task_name'] = task_name
        server_args['task_id'] = self.request.id
        server_args['max_number'] = number
        server_args['zoomeye_search_type'] = search_type
        NewScan(server_args)
    if api_name == 'baidu':
        server_args['baidu'] = keyword
        server_args['custom_scripts'] = script
        server_args['task_name'] = task_name
        server_args['task_id'] = self.request.id
        server_args['max_number'] = number
        NewScan(server_args)



@celery.task(bind=True)
def FileScanTask(self,file_path,script,task_name):
    server_args = GetSeverArgs()
    server_args['custom_scripts'] = script
    server_args['task_name'] = task_name
    server_args['task_id'] = self.request.id
    server_args['target_file'] = file_path
    NewScan(server_args)