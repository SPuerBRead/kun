# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : models.py

from flask_mongoengine import MongoEngine
from datetime import datetime

db = MongoEngine()

class Task(db.Document):
    task_id = db.StringField(required = True)
    task_name = db.StringField()
    short_target = db.StringField()
    full_target = db.StringField()
    scan_mode = db.StringField()
    target_type = db.StringField()
    script_type = db.StringField()
    target_number = db.IntField()
    script_info = db.StringField()
    start_time = db.DateTimeField(default=datetime.now)
    finish_time = db.DateTimeField(default=datetime.now)

class Result(db.Document):
    task_id = db.StringField(required = True,unique=True)
    result = db.StringField()
    high_count = db.IntField()
    medium_count = db.IntField()
    low_count = db.IntField()

class Script(db.Document):
    script_id = db.StringField(required = True,unique=True)
    script_name = db.StringField()
    script_info = db.StringField()
    script_author = db.StringField()
    script_update_time = db.StringField()
    script_level = db.StringField()
    script_title = db.StringField()

class Status(db.Document):
    task_id = db.StringField(required = True,unique=True)
    task_name = db.StringField()
    warning = db.StringField()
    status = db.StringField()
    progress = db.StringField()
    create_time = db.DateTimeField(default=datetime.now)

class Vuln(db.Document):
    task_id = db.StringField(required=True)
    vuln_id = db.StringField(required=True, unique=True)
    target = db.StringField()
    script = db.StringField()
    message = db.StringField()
    script_type = db.StringField()
    create_time = db.DateTimeField(default=datetime.now)


class User(db.Document):
    username = db.StringField(required=True, max_length=64)
    password = db.StringField(max_length=256)

    is_authenticated = True

    is_active = True

    is_anonymous = True


    def get_id(self):
        return str(self.id)

    def __unicode__(self):
        return self.username