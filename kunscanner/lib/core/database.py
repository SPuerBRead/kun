# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午6:41
# @author : Xmchx
# @File   : database.py

from data import args
from models import Task,Result,Status,Vuln, ConnectDatabase
from enums import TARGET_TYPE,STATUS
import json
import hashlib
from exception import DatabaseException

def CheckDatabase():
    return ConnectDatabase()



def SaveTaskToDatabase():
    if args.use_database == False:
        return
    if args.scan_type == TARGET_TYPE.API:
        target_type = args.scan_type + ' ' + args.api_type
    else:
        target_type = args.scan_type
    try:
        Task(
            task_id=args.task_id,
            task_name=args.task_name,
            short_target=args.user_input_target,
            scan_mode=args.scanner_mode,
            target_type=target_type,
            script_type=args.script_type,
        ).save()

        Result(
            task_id=args.task_id,
            result='',
            high_count = 0,
            medium_count = 0,
            low_count = 0
        ).save()
    except Exception,e:
        raise DatabaseException(repr(e))


def UpdataSpiderScanInfoToDatabase(target_list,script_loader):
    if args.use_database == False:
        return
    script_list = []
    try:
        for script in script_loader.script_object_list:
            script_list.append(script['name'])
        if Task.objects(task_id = args.task_id).count():
            task = Task.objects(task_id=args.task_id)
            task.update(
                full_target=json.dumps(target_list),
                target_number=str(len(target_list)),
                script_info=json.dumps(script_list)
            )
    except Exception,e:
        raise DatabaseException(repr(e))

def UpdateCommonScanInfoToDatabase(target_loader,script_loader):
    if args.use_database == False:
        return
    script_list = []
    try:
        for script in script_loader.script_object_list:
            script_list.append(script['name'])
        if Task.objects(task_id = args.task_id).count():
            task = Task.objects(task_id = args.task_id)
            task.update(
                full_target = json.dumps(target_loader.domain_list),
                target_number = str(len(target_loader.domain_list)),
                script_info = json.dumps(script_list)
            )
    except Exception,e:
        raise DatabaseException(repr(e))

def UpdateStatus():
    if args.use_database == False:
        return
    try:
        if Status.objects(task_id=args.task_id).count():
            status = Status.objects(task_id=args.task_id).first()
            status.update(status=STATUS.RUN)
        else:
            try:
                Status(
                    task_id=args.task_id,
                    task_name=args.task_name,
                    warning='',
                    progress='0',
                    status=STATUS.RUN
                ).save()
            except Exception,e:
                if 'duplicate key' in e:
                    pass
    except Exception,e:
        raise DatabaseException(repr(e))


def SaveWarningToDatabase(data):
    if args.use_database == False:
        return
    try:
        status = Status.objects(task_id = args.task_id)
        status.update(warning = data)
    except Exception,e:
        raise DatabaseException(repr(e))



def SaveProgressToDatabase(data):
    if args.use_database == False:
        return
    try:
        status = Status.objects(task_id = args.task_id)
        status.update(progress = data)
    except Exception,e:
        raise DatabaseException(repr(e))


def SaveStatusToDatabase(data):
    if args.use_database == False:
        return
    try:
        status = Status.objects(task_id = args.task_id)
        status.update(status = data)
    except Exception,e:
        raise DatabaseException(repr(e))


'''
扫描任务最终结果的格式
[{
	"target": "127.0.0.1",
	"result": [{
		"items": {
			"test1": "test1",
			"test2": "test2",
			"test3": ""
		},
		"script_name": "web_info",
		"script_type": "info"
	}, {
		"message": "",
		"script_name": "redis_unauth",
		"script_type": "attack"
	}]
}, {
	"target": "127.0.0.2",
	"result": [{
		"items": {
			"test1": "test1",
			"test2": "test2",
			"test3": ""
		},
		"script_name": "web_info",
		"script_type": "info"
	}]
}]
'''


def SaveResultToDatabase(data):
    if args.use_database == False:
        return
    if not len(data['result']):
        return
    try:
        result = Result.objects(task_id = args.task_id)
        result.update(
            result = json.dumps(data['result']),
            high_count = data['high_count'],
            medium_count = data['medium_count'],
            low_count = data['low_count'])
        for each in data['result']:
            for script in each['result']:
                if script['script_type'] == 'attack':
                    vuln_id = hashlib.md5(each['target'] + script['script_name']).hexdigest()
                    if Vuln.objects(vuln_id=vuln_id).count() == 0:
                        Vuln(
                            task_id=args.task_id,
                            vuln_id=vuln_id,
                            target=each['target'],
                            script=hashlib.md5(script['script_name']).hexdigest(),
                            message=script['message'],
                            script_type=script['script_type']
                        ).save()
                    else:
                        vuln = Vuln.objects(vuln_id=vuln_id).first()
                        vuln.update(task_id=args.task_id,target=each['target'],script=hashlib.md5(script['script_name']).hexdigest(),
                                   message=script['message'],script_type=script['script_type'])
                elif script['script_type'] == 'info':
                    vuln_id = hashlib.md5(each['target'] + script['script_name']).hexdigest()
                    if Vuln.objects(vuln_id=vuln_id).count() == 0:
                        Vuln(
                            task_id=args.task_id,
                            vuln_id=vuln_id,
                            target=each['target'],
                            script=hashlib.md5(script['script_name']).hexdigest(),
                            message=json.dumps(script['items']),
                            script_type = script['script_type']
                        ).save()
                    else:
                        vuln = Vuln.objects(vuln_id = vuln_id).first()
                        vuln.update(task_id=args.task_id,target=each['target'],script=hashlib.md5(script['script_name']).hexdigest(),
                                    message=json.dumps(script['items']),script_type=script['script_type']
                        )
    except Exception,e:
        raise DatabaseException(repr(e))