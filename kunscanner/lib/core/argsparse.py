# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午4:40
# @author : Xmchx
# @File   : argsparse.py

import uuid
import datetime
from data import args, conf
from enums import TARGET_TYPE, API_TYPE, SCRIPT_TYPE, SAVE_DATA_TYPE, SCANNER_MODE, WORK_TYPE
from exception import ArgsException

def SetOptions():
    '''
    设置目标
    '''
    if args.url != None:
        args.scan_type = TARGET_TYPE.SINGLE_URL
        args.user_input_target = args.url

    elif args.target_file != None:
        args.scan_type = TARGET_TYPE.TARGET_FILE
        args.user_input_target = args.target_file

    elif args.ip_segment != None:
        args.scan_type = TARGET_TYPE.IPS
        args.user_input_target = args.ip_segment

    elif args.spider_init_url != None:
        args.scan_type = TARGET_TYPE.SPIDER
        args.user_input_target = args.spider_init_url

    elif args.zoomeye != None:
        args.scan_type = TARGET_TYPE.API
        args.api_type = API_TYPE.ZOOMEYE
        args.user_input_target = args.zoomeye
    elif args.baidu != None:
        args.scan_type = TARGET_TYPE.API
        args.api_type = API_TYPE.BAIDU
        args.user_input_target = args.baidu
    elif args.subdomain != None:
        args.scan_type = TARGET_TYPE.API
        args.api_type = API_TYPE.SUBDOMAIN
        args.user_input_target = args.subdomain
    else:
        args.scan_type = None
    '''
    设置脚本加载方式
    '''
    if args.custom_scripts != None:
        args.script_type = SCRIPT_TYPE.CUSTOM_SCRIPT

    elif args.all_scripts == True:
        args.script_type = SCRIPT_TYPE.ALL_SCRIPT

    else:
        args.script_type = None
    '''
    设置存储方式
    '''
    if conf.SAVE_RESULT_TO_FILE == 'true' and conf.SAVE_RESULT_TO_DATABASE == 'true':
        conf.SAVE_TYPE = SAVE_DATA_TYPE.ALL

    elif conf.SAVE_RESULT_TO_FILE == 'true':
        conf.SAVE_TYPE = SAVE_DATA_TYPE.FILE

    elif conf.SAVE_RESULT_TO_DATABASE == 'true':
        conf.SAVE_TYPE = SAVE_DATA_TYPE.DATABASE

    elif conf.SAVE_RESULT_TO_FILE == 'false' and conf.SAVE_RESULT_TO_DATABASE == 'false':
            conf.SAVE_TYPE = SAVE_DATA_TYPE.NO_OUTPUT
    '''
    设置任务信息
    '''
    if args.scanner_mode == SCANNER_MODE.CONSOLE:
        if conf.SAVE_TYPE == SAVE_DATA_TYPE.DATABASE or conf.SAVE_TYPE == SAVE_DATA_TYPE.ALL:
            args.task_id = str(uuid.uuid1())
            if args.task_name == None:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                args.task_name = now_time
    '''
    设置数据库方式
    '''
    if args.scanner_mode == SCANNER_MODE.WEB or conf.SAVE_TYPE == SAVE_DATA_TYPE.DATABASE or conf.SAVE_TYPE == SAVE_DATA_TYPE.ALL:
        args.use_database = True
    else:
        args.use_database = False
    '''
    检查是否设置目标和脚本
    '''
    if args.scan_type != None and args.script_type == None:
        raise ArgsException('Please enter the attack script. E.g: --script "struts2*"')
    '''
    设定输入命令为扫描还是其他
    '''
    if args.scan_type != None and args.script_type != None:
        args.work_type = WORK_TYPE.SCAN

    elif args.custom_scripts_info != None or args.all_scripts_info == True or args.search_script != None:
        args.work_type = WORK_TYPE.INFO
        if args.custom_scripts_info != None:
            args.custom_scripts = args.custom_scripts_info
            args.script_type = SCRIPT_TYPE.CUSTOM_SCRIPT
        elif args.all_scripts_info == True:
            args.script_type = SCRIPT_TYPE.ALL_SCRIPT
        elif args.search_script != None:
            args.script_type = SCRIPT_TYPE.ALL_SCRIPT


