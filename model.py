#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import web

import pymssql


#db=MSSQL(host='127.0.0.1',db='MyTest',user='sa',pwd='1234')
db=web.database(dbn='mssql',host='127.0.0.1',port=1433,db='MyTest',user='sa',pw='1234')
#不知道为什么web.py db这sqlserver这种查询是[]，数据是有的，发现两次了，只好重写


def list_article():
    '''取文章列表'''
    m = db.query('select * from WK_ARTICLES order by UPDATE_TIME desc').list()
    return m