#coding:utf-8
from __future__ import absolute_import, unicode_literals

#import celery app object
from .celery import app as celery_app
import pymysql
pymysql.install_as_MySQLdb()
from .celery import app as celery_app
