# -*- coding: utf-8 -*-
# @Time   : 2018/4/24 下午2:21
# @author : Xmchx
# @File   : celery_worker.py

from app import CreateApp
from extensions import celery

app = CreateApp()
app.app_context().push()