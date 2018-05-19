# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午2:15
# @author : Xmchx
# @File   : scanner.py


from lib.core.enums import SCANNER_MODE
from lib.core.common import GetSystemType,SysQuit
from lib.core.log import SetLogger
from lib.core import SetConfig, SetPath, SetArgs
from lib.parse.cmdline import CmdLineParser
from lib.core.exception import LoadConfException
from lib.core.argsparse import SetOptions


def Init():
    try:
        GetSystemType()
        SetLogger()
        SetPath()
        SetConfig()
    except LoadConfException:
        SysQuit()


def Main(scanner_mode, scan_args=None):
    Init()
    data = None
    from lib.core.exception import ArgsException, DatabaseException
    try:
        if scanner_mode == SCANNER_MODE.CONSOLE:
            SetArgs(scanner_mode, CmdLineParser())
        else:
            SetArgs(scanner_mode, scan_args)
        SetOptions()
        from lib.controller.controller import Engine
        engine = Engine()
        data = engine.Run()

    except ArgsException:
        SysQuit()
    except DatabaseException:
        SysQuit()
    return data
