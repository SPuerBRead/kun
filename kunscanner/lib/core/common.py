# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午2:41
# @author : Xmchx
# @File   : common.py

import os
import sys
import platform
from data import conf
from enums import SYSTEM_TYPE

def GetSystemType():
    system = platform.system()
    if system == 'Windows':
        conf.SYSTEM_TYPE = SYSTEM_TYPE.WINDOWS
    elif system == 'Linux':
        conf.SYSTEM_TYPE = SYSTEM_TYPE.LINUX
    else:
        conf.SYSTEM_TYPE = SYSTEM_TYPE.UNKNOWN

def SysQuit(quit_type = 0):
    if quit_type == 0:
        sys.exit()
    else:
        os._exit(0)

def LoadDict(file_path):
    data = []
    with open(file_path,'r') as f:
        fdata = f.readlines()
    for line in fdata:
        if line:
            data.append(line.strip())
    return data




