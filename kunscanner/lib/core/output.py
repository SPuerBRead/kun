# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午3:00
# @author : Xmchx
# @File   : output.py

import sys
import time
from data import args, conf, path
from enums import SCANNER_MODE, MESSAGE_LEVEL,SYSTEM_TYPE,LOG_DEFAULT_LEN,SCRIPT_TYPE
from kunscanner.lib.utils.terminalsize import get_terminal_size
from log import ConsoleLogger,FileLogger
from prettytable import PrettyTable
from kunscanner.lib.core.common import Encode

def InfoOutPut2Console(msg,level = None):
    if args.scanner_mode == SCANNER_MODE.WEB:
        return
    msg = Encode(msg)
    if level == None:
        print msg
        return
    width , height = get_terminal_size()
    indentation = width - len(msg)
    if level == MESSAGE_LEVEL.STATUS_LEVEL:
        sys.stdout.write(' '* (indentation-1) + msg+'\r')
        sys.stdout.flush()
    elif level == MESSAGE_LEVEL.INFO_LEVEL:
        ConsoleLogger.Info(msg)
    elif level == MESSAGE_LEVEL.WARNING_LEVEL and conf.CONSOLE_WARNING == 'true':
        ConsoleLogger.Warning(msg)
    elif level == MESSAGE_LEVEL.ERROR_LEVEL:
        ConsoleLogger.Error(msg)



def OutPutPadding(msg,level = None):
    width , height = get_terminal_size()
    if level == MESSAGE_LEVEL.INFO_LEVEL:
        if len(msg)+LOG_DEFAULT_LEN.INFO > width:
            msg_len = (len(msg)+LOG_DEFAULT_LEN.INFO) % width
        else:
            msg_len = len(msg) + LOG_DEFAULT_LEN.INFO
        if conf.SYSTEM_TYPE == SYSTEM_TYPE.WINDOWS:
            padding_num = width-msg_len-1
        else:
            padding_num = width-msg_len
        msg = msg + ' '*padding_num

    if level == MESSAGE_LEVEL.WARNING_LEVEL:
        if len(msg)+LOG_DEFAULT_LEN.WARNING > width:
            msg_len = (len(msg)+LOG_DEFAULT_LEN.WARNING) % width
        else:
            msg_len = len(msg) + LOG_DEFAULT_LEN.WARNING
        if conf.SYSTEM_TYPE == SYSTEM_TYPE.WINDOWS:
            padding_num = width-msg_len-1
        else:
            padding_num = width-msg_len
        msg = msg + ' '*padding_num

    if level == MESSAGE_LEVEL.ERROR_LEVEL:
        if len(msg)+LOG_DEFAULT_LEN.ERROR > width:
            msg_len = (len(msg)+LOG_DEFAULT_LEN.ERROR) % width
        else:
            msg_len = len(msg) + LOG_DEFAULT_LEN.ERROR
        if conf.SYSTEM_TYPE == SYSTEM_TYPE.WINDOWS:
            padding_num = width-msg_len-1
        else:
            padding_num = width-msg_len
        msg = msg+' '*padding_num
    return msg

def WriteLogToFile(msg,level = None):
    if conf.SAVE_LOG_TO_FILE == 'true':
        if level == MESSAGE_LEVEL.INFO_LEVEL:
            FileLogger.Info(msg)
        elif level == MESSAGE_LEVEL.WARNING_LEVEL:
            FileLogger.Warning(msg)
        elif level == MESSAGE_LEVEL.ERROR_LEVEL:
            FileLogger.Error(msg)


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

def OutputFinalResults(data):
    if not len(data):
        return
    id = 0
    table = PrettyTable(['id','target', "script", 'type','result'])
    table.align = 'l'
    for target in data:
        for info in target['result']:
            if info['script_type'] == 'info':
                for key,value in info['items'].items():
                    id+=1
                    table.add_row([str(id), target['target'],info['script_name'],info['script_type'],key+':'+value])
            elif info['script_type'] == 'attack':
                id += 1
                if info['message']:
                    table.add_row([str(id), target['target'],info['script_name'],info['script_type'],info['message']])
                else:
                    table.add_row([str(id), target['target'], info['script_name'], info['script_type'],
                                   'Vulnerability'])
    InfoOutPut2Console('\nThe complete scan results are shown in the following table:')
    InfoOutPut2Console(table)

def WriteResultToFile(data):
    if not len(data):
        return
    result = []
    for target in data:
        for info in target['result']:
            if info['script_type'] == 'info':
                for key,value in info['items'].items():
                    result.append(target['target']+'\t'+info['script_name']+'\t'+info['script_type']+'\t'+key+':'+value)
            elif info['script_type'] == 'attack':
                if info['message']:
                    result.append(target['target']+'\t'+info['script_name']+'\t'+info['script_type']+'\t'+'Vulnerability'+'\t'+info['message'])
                else:
                    result.append(target['target'] + '\t' + info['script_name'] + '\t' + info[
                        'script_type'])
    if args.output_file_name:
        file_name = args.output_file_name
    else:
        file_name = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    rf = open(path.RESULT_PATH + file_name, 'w')
    for line in result:
        rf.writelines(line+'\n')
    rf.close()
    InfoOutPut2Console('\nScan results are saved in file: '+path.RESULT_PATH + file_name)

def OutputScriptInfo(data):
    if args.script_type == SCRIPT_TYPE.CUSTOM_SCRIPT:
        table = PrettyTable(encoding=sys.stdout.encoding)
        for script in data:
            for key,value in script['object'].Info().items():
                table.add_column(key,[value])
    elif args.script_type == SCRIPT_TYPE.ALL_SCRIPT:
        table = PrettyTable(["name", "info","author","time","type","level"],encoding=sys.stdout.encoding)
        for script in data:
            info = script['object'].Info()
            table.add_row([info['name'],info['info'],info['author'],
                           info['time'],info['type'],info['level']])
    InfoOutPut2Console(table)

def OutPutSearchScriptInfo(data):
    is_exit = False
    table = PrettyTable(["name", "info", "author", "time", "type", "level"])
    for script in data:
        info = script['object'].Info()
        if args.search_script in info['name'] or args.search_script in info['info']:
            is_exit = True
            table.add_row([info['name'], info['info'], info['author'],
                           info['time'], info['type'], info['level']])
    if is_exit:
        InfoOutPut2Console(table)
    else:
        InfoOutPut2Console('No matching Poc found', MESSAGE_LEVEL.INFO_LEVEL)




