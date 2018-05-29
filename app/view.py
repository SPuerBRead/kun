# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : view.py


import os
import cgi
import json
import re
import urlparse
import hashlib
import time
from collections import OrderedDict

from flask import (Blueprint, redirect, render_template, request,
                   url_for)
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import celery
from models import Result, Script, Status, Task, User, Vuln
from task import UrlScanTask, IPSScanTask, SpiderScanTask, ApiScanTask, FileScanTask
from kunscanner.webapi import ScriptsInfo, APIInfo
from data import TASKTYPE,STATUS,APINAME

kun = Blueprint('kun', __name__)

page_item_number = 28

UPLOAD_FOLDER = './app/files'


@kun.route('/', methods=['GET'])
def Root():
    if User.objects().all().count() == 0:
        return redirect(url_for('kun.CreateAdmin'))
    else:
        if current_user.is_authenticated:
            return redirect(url_for('kun.IndexHander'))
        else:
            return redirect(url_for('kun.Login'))


@kun.route('/index',methods=['GET'])
@login_required
def IndexHander():
    return render_template('index.html')

@kun.route('/vuln',methods=['GET'])
@login_required
def VulnHandler():
    return render_template('vuln.html')

@kun.route('/task',methods=['GET'])
@login_required
def TaskHandler():
    return render_template('task.html')

@kun.route('/script',methods=['GET'])
@login_required
def ScriptHandler():
    return render_template('plugin.html')

@kun.route('/task_detail',methods=['GET'])
@login_required
def TaskDetail():
    return render_template('taskDetail.html')


@kun.route('/login',methods=['GET', 'POST'])
def Login():
    login_message = {}
    if request.method == 'GET':
        if current_user.is_authenticated == False:
            return render_template('login.html')
        else:
            return redirect(url_for('kun.IndexHander'))
    if request.method == 'POST':
        data = json.loads(request.get_data())
        username = data['username']
        password = data['password']
        user = User.objects(username=username).first()
        if user:
            if not check_password_hash(user.password, password):
                login_message['success'] = False
                login_message['message'] = u'用户名或密码错误'
                return json.dumps(login_message)
        else:
            login_message['success'] = False
            login_message['message'] = u'用户名或密码错误'
            return json.dumps(login_message)
        login_user(user)
        login_message['success'] = True
        login_message['message'] = u'登陆成功'
        return json.dumps(login_message)

@kun.route('/logout',methods=['GET'])
@login_required
def Logout():
    result = {}
    try:
        logout_user()
        result['success'] = True
    except:
        result['success'] = False
    return json.dumps(result)


@kun.route('/create_admin',methods=['GET', 'POST'])
def CreateAdmin():
    register_message = {}
    if request.method == 'GET':
        if User.objects().all().count() == 0:
            return render_template('regist.html')
        else:
            return redirect(url_for('kun.Login'))
    if request.method == 'POST':
        if User.objects().all().count() == 0:
            data = json.loads(request.get_data())
            username = data['username']
            password = data['password']
            confirm_password = data['confirm_password']
            if not re.match(re.compile(r'^[A-Za-z0-9-]+$'),username):
                register_message['success'] = False
                register_message['message'] = u'用户名只允许使用数字或字母，不允许使用特殊符号。'
                return json.dumps(register_message)
            if password != confirm_password:
                register_message['success'] = False
                register_message['message'] = u'两次输入的密码不相同'
                return json.dumps(register_message)
            if len(password) < 6 or not re.match(re.compile(r'([0-9]+(\W+|\_+|[A-Za-z]+))+|([A-Za-z]+(\W+|\_+|\d+))+|((\W+|\_+)+(\d+|\w+))+'),password):
                register_message['success'] = False
                register_message['message'] = u'密码长度至少为6位，且需要字母，数字，特殊符号至少两种的组合。'
                return json.dumps(register_message)
            pass_hash = generate_password_hash(password, method='pbkdf2:sha256')

            User(
                username = username,
                password = pass_hash
            ).save()
            
            register_message['success'] = True
            register_message['message'] = u'注册成功，请登录'
            return json.dumps(register_message)
        else:
            register_message['success'] = False
            register_message['message'] = u'注册功能在成功注册一次后不能再次使用，请管理员登陆后使用“添加用户”功能添加新用户'
            return json.dumps(register_message)

@kun.route('/user',methods=['GET'])
@login_required
def GetUser():
    result = {}
    result['username'] = current_user.username
    return json.dumps(result)

@kun.route('/add_user',methods=['POST'])
@login_required
def AddUser():
    register_message = {}
    data = json.loads(request.get_data())
    username = data['username']
    password = data['password']
    confirm_password = data['confirm_password']
    if password != confirm_password:
        register_message['success'] = False
        register_message['message'] = u'两次输入的密码不相同'
    if User.objects(username=username).all().count():
        register_message['success'] = False
        register_message['message'] = u'用户名已被使用。'
        return json.dumps(register_message)
    if not re.match(re.compile(r'^[A-Za-z0-9-]+$'),username):
        register_message['success'] = False
        register_message['message'] = u'用户名只允许使用数字或字母，不允许使用特殊符号。'
        return json.dumps(register_message)
    if len(password) < 6 or not re.match(re.compile(r'([0-9]+(\W+|\_+|[A-Za-z]+))+|([A-Za-z]+(\W+|\_+|\d+))+|((\W+|\_+)+(\d+|\w+))+'),password):
        register_message['success'] = False
        register_message['message'] = u'密码长度至少为6位，且需要字母，数字，特殊符号至少两种的组合。'
        return json.dumps(register_message)
    pass_hash = generate_password_hash(password, method='pbkdf2:sha256')
    User(
        username = username,
        password = pass_hash
    ).save()
    register_message['success'] = True
    register_message['message'] = u'注册成功，请登录'
    return json.dumps(register_message)

@kun.route('/task_list/<string:show_type>', methods=['GET'])
@login_required
def TaskList(show_type):
    result = []
    page_result = {}
    if show_type == 'index':
        lens = len(Status.objects)
        if lens > 10:
            data = Status.objects[lens - 10:lens]
        else:
            data = Status.objects().all()
    elif show_type == 'all':
        data = Status.objects().all()
    elif show_type == 'page':
        page_number = int(request.args.get('p'))
        lens = len(Status.objects)
        page_result['total_page'] = str(lens//page_item_number+1)
        if page_number > lens//page_item_number+1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            data = Status.objects[lens-(page_number*page_item_number):lens-(page_item_number*(page_number-1))]
        else:
            data = Status.objects[0 :lens-(page_item_number*(page_number-1))]
    for each in data:
        info = {}
        info['create_time'] = str(each.create_time).split('.')[0]
        info['task_name'] = cgi.escape(each.task_name)
        info['task_id'] = each.task_id
        info['status'] = each.status
        info['progress'] = each.progress
        info['warning'] = each.warning
        result.append(info)
    result.reverse()
    if show_type == 'page':
        page_result['info'] = result
        return json.dumps(page_result)
    return json.dumps(result)

@kun.route('/vuln_list/<string:show_type>', methods=['GET'])
@login_required
def VulnList(show_type):
    result = []
    page_result = {}
    if show_type == 'index':
        data = Vuln.objects.item_frequencies('script', normalize=True)
        data = OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        for script_id, percent in data.items():
            info = {}
            info['script'] = Script.objects(script_id=script_id).first().script_name
            info['count'] = str(Vuln.objects(script=script_id).count())
            info['percent'] = "%.02f%%" % (percent * 100)
            result.append(info)
        if len(result) > 10:
            result = result[0:10]
    elif show_type == 'all':
        data = Vuln.objects().all()
        for each in data:
            info = {}
            script = Script.objects(script_id=each.script).first()
            try:
                info['task_name'] = cgi.escape(Task.objects(task_id=each.task_id).first().task_name)
            except:
                info['task_name'] = u'该任务已删除，无法查看'
            info['task_id'] = each.task_id
            info['target'] = each.target
            info['script_name'] = script.script_name
            info['script_id'] = each.script
            info['message'] = each.message
            info['script_type'] = each.script_type
            info['time'] = str(each.create_time).split('.')[0]
            info['level'] = script.script_level
            result.append(info)
        result.reverse()
    elif show_type == 'page':
        page_number = int(request.args.get('p'))
        lens = len(Vuln.objects)
        page_result['total_page'] = str(lens//page_item_number+1)
        if page_number > lens//page_item_number+1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            data = Vuln.objects[lens-(page_number*page_item_number):lens-(page_item_number*(page_number-1))]
        else:
            data = Vuln.objects[0 :lens-(page_item_number*(page_number-1))]
        for each in data:
            info = {}
            script = Script.objects(script_id=each.script).first()
            try:
                info['task_name'] = cgi.escape(Task.objects(task_id=each.task_id).first().task_name)
            except:
                info['task_name'] = u'该任务已删除，无法查看'
            info['task_id'] = each.task_id
            info['target'] = each.target
            info['script_name'] = script.script_name
            info['script_id'] = each.script
            info['message'] = each.message
            info['script_type'] = each.script_type
            info['time'] = str(each.create_time).split('.')[0]
            info['level'] = script.script_level
            result.append(info)
        result.reverse()
        page_result['info'] = result
        return json.dumps(page_result)
    return json.dumps(result)

@kun.route('/get_scripts', methods=['GET'])
@login_required
def GetScripts():
    result = []
    scripts = Script.objects().all()
    for script in scripts:
        info = {}
        info['name'] = script.script_name
        info['id'] = script.script_id
        result.append(info)
    return json.dumps(result)

#3
@kun.route('/script_list/<string:show_type>',methods=['GET'])
@login_required
def ScriptList(show_type):
    result = []
    page_result={}
    if show_type == 'index':
        data = Vuln.objects.item_frequencies('script', normalize=True)
        data = OrderedDict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        for script_id,percent in data.items():
            script = Script.objects(script_id=script_id).first()
            info = {}
            info['name'] = script.script_name
            info['create_time'] = script.script_update_time
            info['author'] = script.script_author
            info['title'] = script.script_title
            info['level'] = script.script_level
            result.append(info)
        if len(result) > 10:
            result = result[0:10]
    elif show_type == 'all':
        data = Script.objects.all()
        for each in data:
            info = {}
            info['id'] = each.script_id
            info['detail'] = each.script_info
            info['create_time'] = each.script_update_time
            info['author'] = each.script_author
            info['level'] = each.level
            result.append(info)
        result.reverse()
    elif show_type == 'page':
        page_number = int(request.args.get('p'))
        lens = len(Script.objects)
        page_result['total_page'] = str(lens//page_item_number+1)
        if page_number > lens//page_item_number+1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            data = Script.objects[lens-(page_number*page_item_number):lens-(page_item_number*(page_number-1))]
        else:
            data = Script.objects[0 :lens-(page_item_number*(page_number-1))]
        for each in data:
            info = {}
            info['id'] = each.script_id
            info['detail'] = each.script_info
            info['create_time'] = each.script_update_time
            info['author'] = each.script_author
            info['level'] = each.script_level
            info['count'] = Vuln.objects(script=each.script_id).count()
            info['title'] = each.script_title
            result.append(info)
        result.reverse()
        page_result['info'] = result
        return json.dumps(page_result)
    return json.dumps(result)


@kun.route('/task_count',methods=['GET'])
@login_required
def TaskCount():
    result = {}
    result['running'] = str(Status.objects(status = STATUS.RUN).count())
    result['waiting'] = str(Status.objects(status=STATUS.WAIT).count())
    result['finish'] = str(Status.objects(status=STATUS.FINISH).count())
    result['fail'] = str(Status.objects(status=STATUS.FAIL).count())
    return json.dumps(result)


@kun.route('/api_list',methods=['GET'])
@login_required
def index():
    return json.dumps(APIInfo())


# #获得任务结果
# @kun.route('/task_result/<string:task_id>',methods=['GET'])
# @login_required
# def TaskResult(task_id):
#     query_message = {}
#     if not Result.objects(task_id=task_id).first():
#         query_message['success'] = False
#         query_message['message'] = 'Task_id does not exist or the task has not been completed'
#         return json.dumps(query_message)
#     result = Result.objects(task_id=task_id).first()
#     return result['result']

# #获得任务状态
# @kun.route('/task_status/<string:task_id>',methods=['GET'])
# @login_required
# def TaskStatus(task_id):
#     query_message = {}
#     if not Result.objects(task_id=task_id).first():
#         query_message['success'] = False
#         query_message['message'] = 'Task_id does not exist'
#         return json.dumps(query_message)
#     status = Status.objects(task_id=task_id).first()
#     return status.to_json()

#更新插件信息至数据库
@kun.route('/script_update',methods=['GET'])
@login_required
def ScriptUpdate():
    message = {}
    try:
        scripts_info = ScriptsInfo()
        Script.objects().delete()
        for script in scripts_info:
            if Script.objects(script_id = hashlib.md5(script['name']).hexdigest()).count() == 0:
                Script(
                    script_id=hashlib.md5(script['name']).hexdigest(),
                    script_name=script['name'],
                    script_info=script['info'],
                    script_author=script['author'],
                    script_update_time=script['time'],
                    script_level=script['level'],
                    script_title=script['title']
                ).save()
    except:
        message['success'] = False
        return json.dumps(message)
    message['success'] = True
    message['message'] = time.strftime("%Y/%m.%d %H:%M:%S", time.localtime())
    return json.dumps(message)


@kun.route('/celery_task_status/<task_id>',methods=['GET'])
@login_required
def GetTaskStatusFromCelery(task_id):
    message = {}
    task = celery.AsyncResult(task_id)
    message['status'] = task.state
    return json.dumps(message)




@kun.route('/add_task',methods=['POST'])
@login_required
def AddNewTask():
    try:
        data = json.loads(request.get_data())
        task_type = data['task_type']
        task_name = data['task_name']
    except:
        task_type = request.form['task_type']
        task_name = request.form['task_name']
    result = CheckTaskName(task_name)
    if result != True:
        return json.dumps(result)
    if task_type == TASKTYPE.URL:
        target = data['target']
        script = data['script']
        message = AddUrlTask(target,script,task_name)
    if task_type == TASKTYPE.IPS:
        target = data['target']
        script = data['script']
        message = AddIpsTask(target, script, task_name)
    if task_type == TASKTYPE.SPIDER:
        target = data['target']
        script = data['script']
        try:
            number = int(data['number'])
        except:
            number = None
        message = AddSpiderTask(target, script, task_name,number)
    if int(task_type) == TASKTYPE.FILE:
        script = request.form['script']
        file = request.files['file']
        file_path = FileUpload(file)
        message = AddFileTask(file_path,script,task_name)
    if int(task_type) == TASKTYPE.API:
        print 1
        keyword = None
        number = None
        search_type = None
        file_path = None
        try:
            api_name = data['api_name']
        except:
            api_name = request.form['api_name']
        if api_name == APINAME.SUBDOMAIN:
            file = request.files['file']
            file_path = FileUpload(file)
            script = request.form['script']
        else:
            keyword = data['keyword']
            script = data['script']
            try:
                number = int(data['number'])
            except:
                number = None
            if api_name == APINAME.ZOOMEYE:
                try:
                    search_type = data['search_type']
                except:
                    search_type = None
            else:
                search_type = None
        message = AddApiTask(api_name,keyword,script,task_name,number,search_type,file_path)
    return json.dumps(message)

def AddUrlTask(target,scripts,task_name):
    message = {}
    if CheckIp(target) == False and CheckDomain(target) == False:
        message['success'] = False
        message['message'] = u'输入目标不合法，请重新输入'
        return message
    scripts_name = ScriptIdToScriptName(scripts)
    result = CheckScript(scripts_name)
    if result != True:
        return result
    task = UrlScanTask.apply_async(args=[target,scripts_name,task_name])
    message = CreateTaskToDatabase(task.id, task_name)
    return message

def AddIpsTask(target,scripts,task_name):
    message = {}
    if '-' not in target and '/' not in target:
        message['success'] = False
        message['message'] = u'输入目标不合法，请重新输入'
        return message
    scripts_name = ScriptIdToScriptName(scripts)
    result = CheckScript(scripts_name)
    if result != True:
        return result
    task = IPSScanTask.apply_async(args=[target, scripts_name, task_name])
    message = CreateTaskToDatabase(task.id, task_name)
    return message

def AddSpiderTask(target,scripts,task_name,number):
    message = {}
    if CheckIp(target) == False and CheckDomain(target) == False:
        message['success'] = False
        message['message'] = u'输入目标不合法，请重新输入'
        return message
    scripts_name = ScriptIdToScriptName(scripts)
    result = CheckScript(scripts_name)
    if result != True:
        return result
    task = SpiderScanTask.apply_async(args=[target, scripts_name, task_name,number])
    message = CreateTaskToDatabase(task.id, task_name)
    return message

def AddApiTask(api_name,keyword,scripts,task_name,number,search_type,file_path):
    message = {}
    if api_name == APINAME.ZOOMEYE:
        search_type_list = ['web','host']
        if search_type not in search_type_list and search_type:
            message['success'] = False
            message['message'] = u'API 搜索类型不正确'
            return message
    if api_name not in APIInfo():
        message['success'] = False
        message['message'] = u'没有找到当前选择的API'
        return message
    scripts_name = ScriptIdToScriptName(scripts)
    result = CheckScript(scripts_name)
    if result != True:
        return result
    if api_name == APINAME.ZOOMEYE or api_name == APINAME.BAIDU:
        if not keyword:
            message['success'] = False
            message['message'] = u'请输入查询API的关键字'
            return message
    task = ApiScanTask.apply_async(args=[api_name, keyword, scripts_name, task_name, number,search_type,file_path])
    message = CreateTaskToDatabase(task.id, task_name)
    return message

def AddFileTask(file_path,scripts,task_name):
    scripts_name = ScriptIdToScriptName(scripts)
    result = CheckScript(scripts_name)
    if result != True:
        return result
    task = FileScanTask.apply_async(args=[file_path, scripts_name, task_name])
    message = CreateTaskToDatabase(task.id, task_name)
    return message

def FileUpload(file):
    ext = file.filename.rsplit('.', 1)[1]
    now_time = lambda:int(round(time.time() * 1000))
    file_name = str(now_time())+'.'+ext
    file.save(os.path.join(UPLOAD_FOLDER, file_name))
    return os.path.join(UPLOAD_FOLDER, file_name)

def CreateTaskToDatabase(task_id,task_name):
    message = {}
    AddTaskToDataBase(task_id, task_name)
    message['success'] = True
    message['message'] = u'创建扫描任务成功'
    return message


def CheckTaskName(task_name):
    message = {}
    if not task_name:
        message['success'] = False
        message['message'] = u'请输入本次扫描的任务名称'
        return message
    else:
        return True


def CheckScript(scripts_name):
    message = {}
    if scripts_name == '':
        message['success'] = False
        message['message'] = u'没有找到选择的部分脚本，可能是脚本更新但数据库没有更新导致，请点击用户栏“更新插件”按钮，对插件列表进行更新'
        return message
    else:
        return True



def ScriptIdToScriptName(scripts):
    md5_reg = r'^[a-z0-9]{32}'
    script_list = []
    script_tmp = []
    if ',' in scripts:
        script_list = scripts.split(',')
    else:
        if re.match(re.compile(md5_reg),scripts):
            script_list.append(scripts)
    for script_id in script_list:
        if re.match(re.compile(md5_reg),script_id):
            script = Script.objects(script_id=script_id).first()
            if script == None:
                return ''
            script_tmp.append(script.script_name)
        else:
            return ''
    scripts_name = ','.join(script_tmp)

    return scripts_name

def CheckIp(ip):
    if not ip.startswith('http'):
        ip = 'http://' + ip
    up = urlparse.urlparse(ip)
    if up.netloc:
        if ':' in up.netloc:
            ip = up.netloc.split(':')[0]
        else:
            ip = up.netloc
    regex = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if regex.match(ip):
        return True
    else:
        return False


def CheckDomain(domain):
    if not domain.startswith('http'):
        domain = 'http://' + domain
    up = urlparse.urlparse(domain)
    if up.netloc:
        if ':' in up.netloc:
            d = up.netloc.split(':')[0]
        else:
            d = up.netloc
    regex = re.compile(r'(?i)^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
    if regex.match(d):
        return True
    else:
        return False


def AddTaskToDataBase(task_id,task_name):
    if not Status.objects(task_id=task_id).count():
        Status(
            task_id=task_id,
            task_name=task_name,
            warning='',
            progress='0',
            status='Waiting'
        ).save()

@kun.route('/task_delete/<string:task_id>',methods=['GET'])
@login_required
def DeleteTask(task_id):
    result = {}
    if Status.objects(task_id=task_id).count():
        status = Status.objects(task_id=task_id).first()
        if status.status == STATUS.WAIT or status.status == STATUS.RUN:
            try:
                celery.control.revoke(task_id,terminate=True)
                status.update(status=STATUS.CLOSE)
                result['success'] = True
            except:
                result['success'] = False
        else:
            try:
                status.delete()
                task = Task.objects(task_id=task_id).first()
                if task:
                    task.delete()
                result['success'] = True
            except:
                result['success'] = False
    else:
        result['success'] = False
    return json.dumps(result)

@kun.route('/search/<search_type>',methods=['GET'])
@login_required
def DataSearch(search_type):
    keyword = request.args.get('keyword')
    page_number = int(request.args.get('p'))
    result = []
    page_result = {}
    if search_type == 'script':
        lens = len(Script.objects(__raw__={'script_info': re.compile(keyword)}).all())
        page_result['total_page'] = str(lens // page_item_number + 1)
        if page_number > lens // page_item_number + 1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            scripts = Script.objects(__raw__={'script_info': re.compile(keyword)})[
                    lens - (page_number * page_item_number):lens - (page_item_number * (page_number - 1))]
        else:
            scripts = Script.objects(__raw__={'script_info': re.compile(keyword)})[
                    0:lens - (page_item_number * (page_number - 1))]
        for each in scripts:
            info = {}
            info['id'] = each.script_id
            info['detail'] = each.script_info
            info['create_time'] = each.script_update_time
            info['author'] = each.script_author
            info['level'] = each.script_level
            info['count'] = Vuln.objects(script=each.script_id).count()
            info['title'] = each.script_title
            result.append(info)
    elif search_type == 'task':
        lens = len(Status.objects(__raw__={'task_name': re.compile(keyword)}).all())
        page_result['total_page'] = str(lens // page_item_number + 1)
        if page_number > lens // page_item_number + 1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            tasks = Status.objects(__raw__={'task_name': re.compile(keyword)})[
                    lens - (page_number * page_item_number):lens - (page_item_number * (page_number - 1))]
        else:
            tasks = Status.objects(__raw__={'task_name': re.compile(keyword)})[
                    0:lens - (page_item_number * (page_number - 1))]
        for each in tasks:
            info = {}
            info['create_time'] = str(each.create_time).split('.')[0]
            info['task_name'] = cgi.escape(each.task_name)
            info['task_id'] = each.task_id
            info['status'] = each.status
            info['progress'] = each.progress
            result.append(info)
    elif search_type == 'vuln':
        lens = len(Vuln.objects(__raw__={'target': re.compile(keyword)}).all())
        page_result['total_page'] = str(lens // page_item_number + 1)
        if page_number > lens // page_item_number + 1:
            return json.dumps(page_result)
        if page_number * page_item_number < lens:
            vulns = Vuln.objects(__raw__={'target': re.compile(keyword)})[lens - (page_number * page_item_number):lens - (page_item_number * (page_number - 1))]
        else:
            vulns = Vuln.objects(__raw__={'target': re.compile(keyword)})[0:lens - (page_item_number * (page_number - 1))]
        for each in vulns:
            info = {}
            script = Script.objects(script_id=each.script).first()
            try:
                info['task_name'] = cgi.escape(Task.objects(task_id=each.task_id).first().task_name)
            except:
                info['task_name'] = u'该任务已删除，无法查看'
            info['task_id'] = each.task_id
            info['target'] = each.target
            info['script_name'] = script.script_name
            info['script_id'] = each.script
            info['message'] = each.message
            info['script_type'] = each.script_type
            info['time'] = str(each.create_time).split('.')[0]
            info['level'] = script.script_level
            result.append(info)
    page_result['info'] = result
    return json.dumps(page_result)

@kun.route('/task_info/<string:task_id>',methods=['GET'])
@login_required
def TaskInfo(task_id):
    result = {}
    result['info'] = {}
    status = Status.objects(task_id=task_id).first()
    if not status:
        result['success'] = False
        result['message'] = u'任务ID不存在。'
        return json.dumps(result)
    if status.status == STATUS.WAIT:
        result['success'] = False
        result['message'] = u'任务尚未开始，请等待。'
        return json.dumps(result)
    if status.status == STATUS.RUN:
        result['success'] = False
        result['message'] = u'扫描正在进行中，请等待。'
        return json.dumps(result)
    if status.status == STATUS.CLOSE:
        result['success'] = False
        result['message'] = u'该任务已关闭，无法查看。'
        return json.dumps(result)
    if status.status == STATUS.FAIL:
        result['success'] = False
        result['message'] = str(status.warning)
        return json.dumps(result)
    task = Task.objects(task_id = task_id).first()
    if not task:
        result['success'] = False
        result['message'] = u'任务ID不存在.'
        return json.dumps(result)
    scan_result = Result.objects(task_id=task_id).first()
    result['info']['task_name'] = cgi.escape(task.task_name)
    result['info']['input_target'] = task.short_target
    result['info']['scan_mode'] = task.scan_mode
    result['info']['target_type'] = task.target_type
    result['info']['script_type'] = task.script_type
    result['info']['start_time'] = str(task.start_time).split('.')[0]
    result['info']['finish_time'] = str(task.finish_time).split('.')[0]
    result['info']['target_number'] = task.target_number
    result['info']['full_target'] = task.full_target
    result['info']['script_number'] = len(json.loads(task.script_info))
    result['info']['high_count'] = scan_result.high_count
    result['info']['medium_count'] = scan_result.medium_count
    result['info']['low_count'] = scan_result.low_count
    result['info']['result'] = scan_result.result
    scripts_list = []
    for script_name in json.loads(task.script_info):
        script_data = {}
        script = Script.objects(script_name=script_name).first()
        script_data['script_name'] = script_name
        script_data['script_title'] = script.script_title
        script_data['script_id'] = script.script_id
        script_data['script_level'] = script.script_level
        scripts_list.append(script_data)
    result['info']['scripts_info'] = scripts_list
    result['info']['warning'] = status.warning
    result['success'] = True
    result['message'] = ''
    return json.dumps(result)

@kun.route('/scanner_data',methods=['GET'])
@login_required
def DataInfo():
    result = {}
    result['vuln_count'] = Vuln.objects().all().count()
    result['script_count'] = Script.objects.all().count()
    return json.dumps(result)


@kun.route('/script_vuln_info/<string:script_id>',methods=['GET'])
@login_required
def ScriptVulnInfo(script_id):
    page_number = int(request.args.get('p'))
    page_result = {}
    result = []
    lens = Vuln.objects(script = script_id).count()
    page_result['total_page'] = str(lens // page_item_number + 1)
    if page_number > lens // page_item_number + 1:
        return json.dumps(page_result)
    if page_number * page_item_number < lens:
        vulns = Vuln.objects(script = script_id)[
                lens - (page_number * page_item_number):lens - (page_item_number * (page_number - 1))]
    else:
        vulns = Vuln.objects(script = script_id)[0:lens - (page_item_number * (page_number - 1))]
    for each in vulns:
        info = {}
        script = Script.objects(script_id=each.script).first()
        try:
            info['task_name'] = cgi.escape(Task.objects(task_id=each.task_id).first().task_name)
        except:
            info['task_name'] = u'该任务已删除，无法查看'
        info['task_id'] = each.task_id
        info['target'] = each.target
        info['script_name'] = script.script_name
        info['script_id'] = each.script
        info['message'] = each.message
        info['script_type'] = each.script_type
        info['time'] = str(each.create_time).split('.')[0]
        info['level'] = script.script_level
        result.append(info)
    page_result['info'] = result
    return json.dumps(page_result)










