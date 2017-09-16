#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from config import *
connWiki = getDataConnection('WIKI')
connWiki = connWiki if connWiki else dbFrame

################################################################################

def list_article(param):
    '''取文章列表'''
    if connWiki:
        usersession = get_userenv()
        dictuser = usersession['userdict']
        str_qry = param.get('qry','')
        str_tag = param.get('tag','')
        clause_where = ['STATUS=0']
        m = []
        if str_qry:
            import copy
            c1 = copy.copy(clause_where)
            c1.append('('+utils.get_where_clause(str_qry,['ART_TITLE'])+')')
            c1 = ' and '.join(c1) if c1 else None
            m = connWiki.select("WK_ARTICLES",vars=locals(),where=c1,order="UPDATE_TIME DESC").list()
            clause_where.append('('+utils.get_where_clause(str_qry,['ART_CONTENT','ART_KEYWORDS','CREATE_USER','UPDATE_USER'])+')')
        if str_tag:
            clause_where.append('('+utils.get_where_clause(str_tag,['ART_KEYWORDS'])+')')
        clause_where = ' and '.join(clause_where) if clause_where else None
        m1 = connWiki.select("WK_ARTICLES",vars=locals(),where=clause_where,order="UPDATE_TIME DESC").list()
        m.extend(m1)
        m = [dict(x, **{"CREATE_NAME":dictuser.get(x['CREATE_USER'],x['CREATE_USER']),
                        "UPDATE_NAME":dictuser.get(x['UPDATE_USER'],x['UPDATE_USER']),
                        "CAN_DEL":x['CREATE_USER']==usersession['usercode'],
                        "CAN_MODI":(x['CREATE_USER']==usersession['usercode'] or (x['CANMODI_USERS'] and usersession['usercode'] and x['CANMODI_USERS'].find(usersession['usercode'])>=0)),
                        "CANMODI_NAMES": ','.join([usersession['userdict'].get(y,y) for y in x['CANMODI_USERS'].split(',')]) if x['CANMODI_USERS'] else '' })
                     for x in m]
        pag_size = param.get('pagsz',5)
        import math
        param['pagtl'] = int(math.ceil(len(m)/5.0))
        pag_curr = web.intget(param.get('pagno',1), 1)
        if pag_curr>param['pagtl']:
            pag_curr = 1
        param['pagno'] = pag_curr
        return m[(pag_curr-1)*pag_size:(pag_curr)*pag_size],len(m)
    else:
        return []

def get_article(artid):
	'''获取文章'''
	if connWiki:
		m = web.listget(connWiki.select("WK_ARTICLES",vars=locals(),where="ART_ID=$artid").list(),0,None)
		if m:
			web.debug("88"*30)
			web.debug(m)
			return m
		else:
			return {"ERROR":'文章不存在!'}
	else:
		return {"ERROR":'No DB!'}
def set_article(param,usercode):
	'''报错文章'''
	if connWiki:
		artid = param.pop('ART_ID','')
		t = connWiki.transaction()
		try:
			if artid:
				param['UPDATE_USER'] = usercode
				param['UPDATE_TIME'] = utils.get_currdatetimestr(connWiki.dbtype)
				connWiki.update("WK_ARTICLES",vars=locals(),where="ART_ID=$artid",**param)
			else:
				artid = utils.get_keyword()
				param['CREATE_USER'] = usercode
				param['CREATE_TIME'] = utils.get_currdatetimestr(connWiki.dbtype)
				param['UPDATE_USER'] = usercode
				param['UPDATE_TIME'] = utils.get_currdatetimestr(connWiki.dbtype)
				connWiki.insert("WK_ARTICLES",ART_ID=artid,**param)
		except Exception, e:
			t.rollback()
			traceback.print_exc()
			return {"ERROR":e}
		else:
			t.commit()
			return {'ART_ID':artid,'MSG':'保存成功！'}
	else:
		return {"ERROR":'No DB!'}

def get_image(imgid):
	'''获取图片'''
	if connWiki:
		m = web.listget(connWiki.select("WK_IMAGES",vars=locals(),where="IMG_ID=$imgid").list(),0,None)
		return m.FILEDATA if m else None
	else:
		return None

def set_image(imgdata,usercode,filename=''):
	'''上传图片'''
	if connWiki:
		#摘要算法简介 imgid类似uuid 是唯一的
		imgid = hashlib.sha1(imgdata).hexdigest()
		web.debug(imgid)
		m = web.listget(connWiki.select("WK_IMAGES",vars=locals(),where="IMG_ID=$imgid").list(),0,None)
		web.debug(m)
		if not m:
			t = connWiki.transaction()
			try:
				connWiki.insert("WK_IMAGES",IMG_ID=imgid,FILEDATA=base64.encodestring(imgdata),FILESIZE=len(imgdata),FILENAME=filename,CREATE_USER=usercode,CREATE_TIME=utils.get_currdatetimestr(connWiki.dbtype))
			except Exception, e:
				t.rollback()
				traceback.print_exc()
				return {"ERROR":e}
			else:
				t.commit()
		return {"IMG_ID":imgid}
	else:
		return {"ERROR":'No DB!'}