# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午3:46
# @author : Xmchx
# @File   : exception.py

from enums import MESSAGE_LEVEL, EXCEPYION_POSITION, STATUS
from output import OutPutPadding,InfoOutPut2Console,WriteLogToFile
from common import Encode

class LoadConfException(Exception):
    def __init__(self,message):
        message = Encode(message)
        msg = OutPutPadding(message,MESSAGE_LEVEL.ERROR_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.ERROR_LEVEL)


class PocWarningException(Exception):
    def __init__(self,target,script,exception):
        target = Encode(target)
        script = Encode(script)
        exception = Encode(exception)
        warning_msg = "Warning in scanner! target: {0} poc: {1} msg: {2}"
        message = warning_msg.format(target,script,exception)
        msg = OutPutPadding(message,MESSAGE_LEVEL.WARNING_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.WARNING_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.WARNING_LEVEL)

class PocErrorException(Exception):
    def __init__(self,message):
        message = Encode(message)
        msg = OutPutPadding(message,MESSAGE_LEVEL.ERROR_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        from database import SaveWarningToDatabase, SaveStatusToDatabase
        SaveStatusToDatabase(STATUS.FAIL)
        SaveWarningToDatabase(message)


class ArgsException(Exception):
    def __init__(self,message):
        message = Encode(message)
        msg = OutPutPadding(message,MESSAGE_LEVEL.ERROR_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        from database import SaveProgressToDatabase, SaveWarningToDatabase, SaveStatusToDatabase
        SaveStatusToDatabase(STATUS.FAIL)
        SaveProgressToDatabase('0')
        SaveWarningToDatabase(message)

class DatabaseException(Exception):
    def __init__(self,message):
        message = Encode(message)
        msg = OutPutPadding(message,MESSAGE_LEVEL.ERROR_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.ERROR_LEVEL)


class APIException(Exception):
    def __init__(self,message):
        message = Encode(message)
        msg = OutPutPadding(message,MESSAGE_LEVEL.ERROR_LEVEL)
        InfoOutPut2Console(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        WriteLogToFile(msg,MESSAGE_LEVEL.ERROR_LEVEL)
        from database import SaveProgressToDatabase, SaveWarningToDatabase, SaveStatusToDatabase
        SaveStatusToDatabase(STATUS.FAIL)
        SaveProgressToDatabase('0')
        SaveWarningToDatabase(message)


class RequestsException():
    def __init__(self,exception,position,error_level,target,script = None):
        self.exception = Encode(repr(exception))
        self.position = Encode(position)
        self.target = Encode(target)
        self.script = Encode(script)
        self.error_level = Encode(error_level)
        if 'ConnectionError' in self.exception:
            self.OutPutMessage('ConnectionError')
        if 'ConnectTimeout' in self.exception or 'ReadTimeout' in self.exception:
            self.OutPutMessage('ConnectTimeout')

    def OutPutMessage(self,exception):
        spider_exception_msg = 'Target: {0} exception: {1}'
        scanner_exception_msg = 'Target: {0} script: {1} exception: {2}'
        api_exception_msg = 'Connect API error exception: {0}'
        if self.position == EXCEPYION_POSITION.SPIDER:
            msg = OutPutPadding(spider_exception_msg.format(self.target,exception),self.error_level)
            InfoOutPut2Console(msg,self.error_level)
            WriteLogToFile(msg,self.error_level)
        elif self.position == EXCEPYION_POSITION.SCANNER:
            msg = OutPutPadding(scanner_exception_msg.format(self.target,self.script,exception),self.error_level)
            InfoOutPut2Console(msg,self.error_level)
            WriteLogToFile(msg,self.error_level)
        elif self.position == EXCEPYION_POSITION.API:
            msg = OutPutPadding(api_exception_msg.format(exception),self.error_level)
            InfoOutPut2Console(msg,self.error_level)
            WriteLogToFile(msg,self.error_level)