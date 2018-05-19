# -*- coding: utf-8 -*-
# @Time   : 2018/3/24 下午6:52
# @author : Xmchx
# @File   : models.py
from datetime import datetime
from data import conf, args
import mongoengine

def ConnectDatabase():
    import socket
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sk.connect((conf.MONGO_HOST, int(conf.MONGO_PORT)))
    except Exception:
        return False
    sk.close()
    return True


if args.use_database == True:
    mongoengine.connect('kun',host=conf.MONGO_HOST, port=int(conf.MONGO_PORT))


class Task(mongoengine.Document):
    task_id = mongoengine.StringField(required=True, unique=True)
    task_name = mongoengine.StringField()
    short_target = mongoengine.StringField()
    full_target = mongoengine.StringField()
    scan_mode = mongoengine.StringField()
    target_type = mongoengine.StringField()
    script_type = mongoengine.StringField()
    target_number = mongoengine.IntField()
    script_info = mongoengine.StringField()
    start_time = mongoengine.DateTimeField(default=datetime.now)
    finish_time = mongoengine.DateTimeField(default=datetime.now)

class Result(mongoengine.Document):
    task_id = mongoengine.StringField(required=True, unique=True)
    result = mongoengine.StringField()
    high_count = mongoengine.IntField()
    medium_count = mongoengine.IntField()
    low_count = mongoengine.IntField()

class Script(mongoengine.Document):
    script_id = mongoengine.StringField(required=True, unique=True)
    script_name = mongoengine.StringField()
    script_info = mongoengine.StringField()
    script_author = mongoengine.StringField()
    script_update_time = mongoengine.StringField()
    script_level = mongoengine.StringField()
    script_title = mongoengine.StringField()

class Status(mongoengine.Document):
    task_id = mongoengine.StringField(required = True,unique=True)
    task_name = mongoengine.StringField()
    warning = mongoengine.StringField()
    status = mongoengine.StringField()
    progress = mongoengine.StringField()
    create_time = mongoengine.DateTimeField(default=datetime.now)

class Vuln(mongoengine.Document):
    task_id = mongoengine.StringField(required=True)
    vuln_id = mongoengine.StringField(required=True, unique=True)
    target = mongoengine.StringField()
    script = mongoengine.StringField()
    message = mongoengine.StringField()
    script_type = mongoengine.StringField()
    create_time = mongoengine.DateTimeField(default=datetime.now)