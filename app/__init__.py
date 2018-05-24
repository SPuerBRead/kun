# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : __init__.py

from flask import Flask
from extensions import celery,login_manager
from view import kun
from models import db

def CreateApp():
    app = Flask(__name__)
    app.config.from_object('config')
    celery.config_from_object('config')
    InitmongoDB(app)
    InitLogin(app)
    RegisterBlueprints(app)
    return app


def RegisterBlueprints(app):
    app.register_blueprint(kun)

def InitmongoDB(app):
    db.init_app(app)

def InitLogin(app):
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.objects(id=user_id).first()