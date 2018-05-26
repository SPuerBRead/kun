# -*- coding: utf-8 -*-
# @Time   : 2018/3/28 下午1:50
# @author : Xmchx
# @File   : info.py

import os
from data import path

def Banner():
    Banner = """
     __
    / /__ __  __ ____
   / //_// / / // __ \\
  / ,<  / /_/ // / / /               author: {0}    version: {1}
 /_/|_| \__,_//_/ /_/                update time: {2}    scripts number: {3}
"""

    update_time = '2018.05.26'
    script_number = ScriptsNumber()
    author = 'Xmchx'
    version = 'v1.2'

    return Banner.format(author,version,update_time,script_number)

def ScriptsNumber():
    count = 0
    for (root, dirs, files) in os.walk(path.SCRIPTS_PATH):
        for f in files:
            if f.split('.')[1] == 'py' and f.split('.')[0] != '__init__':
                count += 1
    return count


