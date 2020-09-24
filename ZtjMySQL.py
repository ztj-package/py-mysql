# -*- coding: utf-8 -*-
# Intro: MySQL实例模块
# Author: Ztj
# Email: ztj1993@gmail.com
# Version: 0.0.3
# Date: 2020-09-08

import os
import time

import pymysql
from DBUtils.PooledDB import PooledDB
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

__version__ = '0.0.3'


class MySQL(object):

    def __init__(self, **kwargs):
        self.pool = None
        self.server = None

        self.options = dict()
        self.options['host'] = kwargs.get('host', os.environ.get('MYSQL_HOST', '127.0.0.1'))
        self.options['port'] = kwargs.get('port', os.environ.get('MYSQL_PORT', 3306))
        self.options['user'] = kwargs.get('user', os.environ.get('MYSQL_USER', 'root'))
        self.options['password'] = kwargs.get('password', os.environ.get('MYSQL_PASSWORD', ''))
        self.options['charset'] = kwargs.get('charset', os.environ.get('MYSQL_CHARSET', 'utf8'))

    def get_pool(self) -> PooledDB:
        if self.pool is None:
            self.pool = PooledDB(creator=pymysql, cursorclass=DictCursor, **self.options)
        return self.pool

    def destroy(self):
        self.pool = None
        self.server = None

    def connection(self) -> Connection:
        return self.get_pool().connection()

    def get_server(self) -> Connection:
        if self.server is None:
            self.server = self.connection()
        return self.server

    def ping(self) -> bool:
        try:
            self.get_server().ping()
            return True
        except:
            return False

    def wait(self, interval_time=60):
        while self.ping() is False:
            time.sleep(interval_time)

    def exec_sql(self, sql):
        connection = self.get_server()
        with connection.cursor() as cursor:
            if isinstance(sql, str):
                cursor.execute(sql)
            else:
                cursor.execute(*sql)
            connection.commit()

    def exec_sql_list(self, sql_list):
        connection = self.get_server()
        with connection.cursor() as cursor:
            for sql in sql_list:
                if isinstance(sql, str):
                    cursor.execute(sql)
                else:
                    cursor.execute(*sql)
            connection.commit()

    def get_record(self, sql, callback, *args, **kwargs):
        connection = self.get_server()
        with connection.cursor() as cursor:
            if isinstance(sql, str):
                cursor.execute(sql)
            else:
                cursor.execute(*sql)
            result = callback(cursor, *args, **kwargs)
        return result

    @staticmethod
    def record_callback_fetch_all(cursor: DictCursor):
        return cursor.fetchall()

    @staticmethod
    def record_callback_fetch_one(cursor: DictCursor):
        return cursor.fetchone()

    @staticmethod
    def record_callback_fetch_value(cursor: DictCursor, field=None):
        row = cursor.fetchone()
        return list(row.values())[0] if field is None else row.get(field)
