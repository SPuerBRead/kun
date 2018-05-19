# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午2:35
# @author : Xmchx
# @File   : __init__.py

import os
from data import path, conf, args
from kunscanner.lib.utils.utils import CheckFileExists,GetConfig
from exception import LoadConfException
from enums import SCANNER_MODE


def SetPath():
    path.START_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    path.ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path.LIB_PATH = path.ROOT_PATH + '/lib/'
    path.DICT_PATH = path.ROOT_PATH + '/dict/'
    path.RESULT_PATH = path.ROOT_PATH + '/result/'
    path.LOG_PATH = path.ROOT_PATH + '/log/'
    path.CONFIG_PATH = path.LIB_PATH + '/config/'
    path.SCRIPTS_PATH = path.LIB_PATH + '/scripts/'


def SetConfig():
    conf.SAVE_LOG_TO_FILE = 'true'
    config_file = 'scanner.conf'
    file_path = path.CONFIG_PATH + config_file
    if CheckFileExists(file_path) == False:
        raise LoadConfException('The {0} file does not exist, The correct path to the file: {1}'.format(config_file, file_path))
    config = GetConfig()
    config.read(file_path)
    for section in config.sections():
        option = config.items(section)
        for opt in option:
            conf.__setitem__(opt[0], opt[1])


def SetArgs(args_type,InputOptions):
    if args_type == SCANNER_MODE.CONSOLE:
        args.update(InputOptions.__dict__)
        args.scanner_mode = SCANNER_MODE.CONSOLE
        args.scan_args = None
    else:
        args.update(InputOptions)
        args.scanner_mode = SCANNER_MODE.WEB
        args.scan_args = InputOptions