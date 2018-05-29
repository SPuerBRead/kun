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
                        help="Load url from ipSegment(e.g. 192.168.0.1-254,192.168.0.1/24,10.10.10.1-10.10.20.255)")

    target.add_argument('-r', metavar='Traget File', dest="target_file", type=str, default=None,
                        help="Load url from file")

    target.add_argument('--number', metavar='Tragte Number', dest="max_number", type=int, default=None,
                     help="Maximum number of targets from the api or spider.")

    spider = parser.add_argument_group('SPIDER')
    spider.add_argument('--spider-url', metavar='Spider URL', dest='spider_init_url', type=str, default=None,
                        help="Spider will start from this domain")

    api = parser.add_argument_group('API')
    api.add_argument('--zoomeye', metavar='Zoomeye Search Keyword', dest="zoomeye", type=str, default=None,
                     help="Use zoomeye api to get the target (e.g. --zoomeye \"port:6379\")")

    api.add_argument('--baidu',metavar='Baidu Search Keyword', dest="baidu", type=str, default=None,
                     help="Use baidu spider to get the target (e.g. --baidu inurl:/user/register)")

    api.add_argument('--subdomain',metavar='subDomainsBrute Result File', dest="subdomain", type=str, default=None,
                     help="Load target from subDomainsBrute Result File (e.g. --subdomain baidu.com_full.txt)")

    api.add_argument('--zt',metavar='Zoomeye Search Type',dest="zoomeye_search_type",type=str,default=None,
                     help="Zoomeye target type web or host,default setting (ZOOMEYE_SEARCH_TYPE)")

    script = parser.add_argument_group('SCRIPT')
    script.add_argument('--script', metavar='Script Name', dest='custom_scripts', type=str, default=None,
                        help='The name of script to use')

    script.add_argument('--script-all', dest='all_scripts', action='store_true',
                        help='Use all script for testing')

    script.add_argument('--script-info', metavar='Script Name Info', dest='custom_scripts_info', type=str, default=None,
                        help='Show the details of the specified attack script')

    script.add_argument('--search',metavar='Search Script', dest='search_script', type=str, default=None,
                        help='Search POC')

    script.add_argument('-s', dest='all_scripts_info', action='store_true',
                        help='Show the details of the specified attack script')

    output = parser.add_argument_group('OUTPUT')
    output.add_argument('-o', metavar='Output File Name',dest='output_file_name', type=str, default=None,
                        help='Show all currently available attack script')

    output.add_argument('--task-name', metavar='Scan Task Name', dest='task_name', type=str, default=None,
                        help='The name of the scan task, only valid when opening the database storage (SAVE_RESULT_TO_DATABASE = true)')

    if len(sys.argv) == 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    return args
