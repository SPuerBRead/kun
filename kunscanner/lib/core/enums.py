# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午2:34
# @author : Xmchx
# @File   : enums.py


class SCANNER_MODE:
    WEB = 'web'
    CONSOLE = 'console'

class SYSTEM_TYPE:
    WINDOWS = 'windows'
    LINUX = 'linux'
    UNKNOWN = 'unknown'

class MESSAGE_LEVEL:
    STATUS_LEVEL = 0
    INFO_LEVEL = 1
    WARNING_LEVEL = 2
    ERROR_LEVEL = 3


class LOG_DEFAULT_LEN:
    INFO = 27
    WARNING = 30
    ERROR = 28


class TARGET_TYPE:
    SINGLE_URL = 'url'
    TARGET_FILE = 'file'
    IPS = 'ip segment'
    SPIDER = 'spider'
    API = 'api'

class API_TYPE:
    ZOOMEYE = 'zoomeye'
    BAIDU = 'baidu'
    SUBDOMAIN = 'subDomainsBrute'

class SCRIPT_TYPE:
    CUSTOM_SCRIPT = "custom script"
    ALL_SCRIPT = "all script"

class SAVE_DATA_TYPE:
    FILE = 0
    DATABASE = 1
    ALL = 2
    NO_OUTPUT = 3

class IPS_TYPE:
    SUBNETMASK = 1
    IPS = 2

class API_LOGIN_TYPE:
    PASSWORD = 0
    ACCESS_TOKEN = 1

class EXCEPYION_POSITION:
    SPIDER = 0
    SCANNER = 1
    API = 2

class SPIDER_TYPE:
    DEPTH_SPIDER = 1
    NUMBER_SPIDER = 2

class WORK_TYPE:
    SCAN = 'scan'
    INFO = 'info'

class STATUS:
    WAIT = 'Waiting'
    RUN = 'Running'
    FINISH = 'Finish'
    FAIL = 'Failed'

class SCRIPT_LEVEL:
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

