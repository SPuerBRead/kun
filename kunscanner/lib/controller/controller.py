# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午3:54
# @author : Xmchx
# @File   : controller.py

import time
from kunscanner.lib.utils.utils import CheckPathAccess
from kunscanner.lib.core.exception import ArgsException, DatabaseException
from kunscanner.lib.core.data import path, conf, args
from kunscanner.lib.core.loader import TargetLoader, ScriptLoader
from kunscanner.lib.core.scanner import Scanner
from kunscanner.lib.core.database import SaveTaskToDatabase, UpdateCommonScanInfoToDatabase, \
    UpdateStatus, CheckDatabase,UpdataSpiderScanInfoToDatabase
from kunscanner.lib.core.output import InfoOutPut2Console,OutputScriptInfo,OutPutSearchScriptInfo
from kunscanner.lib.core.info import Banner
from kunscanner.lib.core.enums import TARGET_TYPE, WORK_TYPE, MESSAGE_LEVEL,SCANNER_MODE

class Engine():
    def __init__(self):
        InfoOutPut2Console(Banner())
        if args.work_type == WORK_TYPE.SCAN:
            InfoOutPut2Console('[!] Starting at ' + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + '\n')
        if CheckPathAccess(path.RESULT_PATH) == False:
            raise ArgsException('Folder: {0} has no written permission'.format(path.RESULT_PATH))
        if CheckPathAccess(path.LOG_PATH) == False:
            raise ArgsException('Folder: {0} has no written permission'.format(path.LOG_PATH))
        if args.use_database == True and args.scanner_mode == SCANNER_MODE.CONSOLE and args.work_type == WORK_TYPE.SCAN:
            InfoOutPut2Console('Connecting to MongoDB', MESSAGE_LEVEL.INFO_LEVEL)
            if CheckDatabase() == False:
                raise DatabaseException('Failed to connect to MongoDB. Please check the MongoDB configuration, or do not use MongoDB (SAVE_RESULT_TO_DATABASE = false)')


    def Run(self):
        if args.work_type == WORK_TYPE.SCAN:
            UpdateStatus()
            SaveTaskToDatabase()
            target_loader = TargetLoader()
            target_loader.Loader()
            script_loader = ScriptLoader()
            script_loader.Loader()

            if args.scan_type == TARGET_TYPE.SPIDER:
                for i in range(int(conf.SCANNER_WAIT_SPIDER_TIME)):
                    if target_loader.spider_info['spider_status'] == True or target_loader.spider_info['domain_queue_sise'] > 10:
                        break
                    else:
                        time.sleep(1)
                if i < int(conf.SCANNER_WAIT_SPIDER_TIME):
                    scanner = Scanner(target_loader, script_loader)
                    scanner.Run()
                    UpdataSpiderScanInfoToDatabase(scanner.spider_target_list,script_loader)
            else:
                UpdateCommonScanInfoToDatabase(target_loader, script_loader)
                scanner = Scanner(target_loader, script_loader)
                scanner.Run()

            InfoOutPut2Console('\n[!] Finish at '+time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

        elif args.work_type == WORK_TYPE.INFO:
            if args.scanner_mode == SCANNER_MODE.CONSOLE:
                if args.search_script != None:
                    OutPutSearchScriptInfo(self.GetScriptsInfo())
                else:
                    OutputScriptInfo(self.GetScriptsInfo())
            if args.scanner_mode == SCANNER_MODE.WEB:
                script_info_list = []
                for script in self.GetScriptsInfo():
                    script_info = {}
                    script_info['name'] = script['object'].Info()['name']
                    script_info['info'] = script['object'].Info()['info']
                    script_info['author'] = script['object'].Info()['author']
                    script_info['time'] = script['object'].Info()['time']
                    script_info['type'] = script['object'].Info()['type']
                    script_info['level'] = script['object'].Info()['level']
                    script_info['title'] = script['object'].Info()['title']
                    script_info_list.append(script_info)
                return script_info_list
            return None


    def GetScriptsInfo(self):
        script_loader = ScriptLoader()
        script_loader.Loader()
        return script_loader.script_object_list


