# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : extensions.py

from celery import Celery,platforms
from config import CELERY_BROKER_URL,CELERY_RESULT_BACKEND
from flask_login import LoginManager

celery = Celery(__name__,broker = CELERY_BROKER_URL,backend=CELERY_RESULT_BACKEND)
platforms.C_FORCE_ROOT = True

login_manager = LoginManager()