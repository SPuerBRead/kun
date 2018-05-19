# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午3:15
# @author : Xmchx
# @File   : log.py

import os
import coloredlogs
import logging


log_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))+'/log/scanner.log'

console_logger = logging.getLogger('console')

file_logger = logging.getLogger('file')


def SetLogger():
    coloredlogs.DEFAULT_LOG_FORMAT = '[%(levelname)s] %(asctime)s %(message)s'
    coloredlogs.DEFAULT_FIELD_STYLES = {
        'levelname': {'color': 'green'},
        'asctime': {'color': 'white', 'Bright': True}
    }
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'info': {'color': 'green'},
        'error': {'color': 'red'},
        'warning': {'color': 'yellow'}
    }
    coloredlogs.install(logger=console_logger)

    file_logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    handler.setFormatter(formatter)
    file_logger.addHandler(handler)


class ConsoleLogger:
    @staticmethod
    def Info(msg):
        console_logger.info(msg)

    @staticmethod
    def Warning(msg):
        console_logger.warning(msg)

    @staticmethod
    def Error(msg):
        console_logger.error(msg)


class FileLogger:
    @staticmethod
    def Info(msg):
        file_logger.info(msg)

    @staticmethod
    def Warning(msg):
        file_logger.warning(msg)

    @staticmethod
    def Error(msg):
        file_logger.error(msg)
