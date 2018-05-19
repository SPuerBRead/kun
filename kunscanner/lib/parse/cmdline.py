# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午4:22
# @author : Xmchx
# @File   : cmdline.py

import sys
import argparse


def CmdLineParser():
    parser = argparse.ArgumentParser()

    target = parser.add_argument_group('TARGET')
    target.add_argument('-u', metavar='URL', dest="url", type=str, default=None,
                        help="Scan a single target (e.g. www.wooyun.org)")

    target.add_argument('-i', metavar='IPS', dest="ip_segment", type=str, default=None,
                        help="Load url from ipSegment(e.g. 192.168.0.1-254,192.168.0.1/24)")

    target.add_argument('-r', metavar='FILE', dest="target_file", type=str, default=None,
                        help="Load url from file")

    target.add_argument('--number', metavar='NUMBER', dest="max_number", type=int, default=None,
                     help="Maximum number of targets from the api or spider.")

    spider = parser.add_argument_group('SPIDER')
    spider.add_argument('--spider-url', metavar='URL', dest='spider_init_url', type=str, default=None,
                        help="Spider will start from this domain")

    api = parser.add_argument_group('API')
    api.add_argument('--zoomeye', metavar='KEYWORD', dest="zoomeye", type=str, default=None,
                     help="Use zoomeye api to get the target (e.g. --zoomeye \"port:6379\")")

    api.add_argument('--zt',metavar='ZOOMEYE SEARCH TYPE',dest="zoomeye_search_type",type=str,default=None,
                     help="Zoomeye target type web or host,default setting (ZOOMEYE_SEARCH_TYPE)")

    script = parser.add_argument_group('SCRIPT')
    script.add_argument('--script', metavar='SCRIPT_NAME', dest='custom_scripts', type=str, default=None,
                        help='The name of script to use')

    script.add_argument('--script-all', dest='all_scripts', action='store_true',
                        help='Use all script for testing')

    script.add_argument('--script-info', metavar='SCRIPT_NAME', dest='custom_scripts_info', type=str, default=None,
                        help='Show the details of the specified attack script')

    script.add_argument('--search',metavar='SEARCH_SCRIPT', dest='search_script', type=str, default=None,
                        help='Search POC')

    script.add_argument('-s', dest='all_scripts_info', action='store_true',
                        help='Show the details of the specified attack script')

    output = parser.add_argument_group('OUTPUT')
    output.add_argument('-o', metavar='FILE_NAME',dest='output_file_name', type=str, default=None,
                        help='Show all currently available attack script')

    output.add_argument('--task-name', metavar='TASK_NAME', dest='task_name', type=str, default=None,
                        help='The name of the scan task, only valid when opening the database storage (SAVE_RESULT_TO_DATABASE = true)')

    if len(sys.argv) == 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    return args
