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
            usersession = get_userenv()
            dictuser = usersession['userdict']
            m["CREATE_NAME"] = dictuser.get(m['CREATE_USER'],m['CREATE_USER'])
            m["UPDATE_NAME"] = dictuser.get(m['UPDATE_USER'],m['UPDATE_USER'])
            m["CAN_MODI"] = (m['CREATE_USER']==usersession['usercode'] or (m['CANMODI_USERS'] and usersession['usercode'] and m['CANMODI_USERS'].find(usersession['usercode'])>=0))
            m["CAN_DEL"] = (m['CREATE_USER']==usersession['usercode'])
            m["CANMODI_NAMES"] = ','.join([usersession['userdict'].get(y,y) for y in m['CANMODI_USERS'].split(',')]) if m['CANMODI_USERS'] else ''
            return m
        else:
            return {"ERROR":'文章不存在!'}
    else:
        return {"ERROR":'No DB!'}
def set_article(param,usercode):
    '''保存文章'''
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
def modi_users(artid,users):
    '''设置文章可修改用户'''
    if not connWiki:
        return {"ERROR":'No DB!'}
    else:
        t = connWiki.transaction()
        try:
            connWiki.update("WK_ARTICLES",vars=locals(),where="ART_ID=$artid",CANMODI_USERS=users)
        except Exception, e:
            t.rollback()
            traceback.print_exc()
            return {"ERROR":e}
        else:
            t.commit()
            return {'ART_ID':artid,'MSG':'保存成功！'}

def increase_readcount(artid):
    '''指定文章的次数加1'''
    if connWiki:
        t = connWiki.transaction()
        try:
            connWiki.update("WK_ARTICLES",vars=locals(),where="ART_ID=$artid",MATCH_TIMES=web.SQLLiteral('MATCH_TIMES+1'))
        except Exception, e:
            t.rollback()
            traceback.print_exc()
            return {"ERROR":e}
        else:
            t.commit()
            return {'ART_ID':artid,'MSG':'保存成功！'}
    else:
        return {"ERROR":'No DB!'}
def get_allkeywords():
    '''得到所有未删除文章的关键词，以{'word':count}形式返回'''
    if connWiki:
        m = connWiki.select("WK_ARTICLES",what="ART_KEYWORDS",where="STATUS=0").list()
        tmpl = []
        for x in m:
            tmpl += x.ART_KEYWORDS.split(' ')
        words = {}
        for x in tmpl:
            if x:
                words[x] = words.get(x,0)+1
        words = sorted(words.iteritems(), key=lambda d:d[1], reverse = True)
        return words
    else:
        return {"ERROR":'No DB!'}
def list_hotarticle(limit=5):
    '''返回阅读次数最多的n篇文章'''
    if connWiki:
        usersession = get_userenv()
        dictuser = usersession['userdict']
        m = connWiki.select("WK_ARTICLES",vars=locals(),where='STATUS=0',order="MATCH_TIMES DESC",limit=limit).list()
        m = [dict(x, **{ "CREATE_NAME":dictuser.get(x['CREATE_USER'],x['CREATE_USER']), "UPDATE_NAME":dictuser.get(x['UPDATE_USER'],x['UPDATE_USER']), "CAN_MODI":x['CREATE_USER']==usersession['usercode'] }) for x in m]
        return m
    else:
        return []
def list_relarticle(article,limit=10):
    '''返回指定文章的相关n篇文章'''
    if connWiki:
        usersession = get_userenv()
        dictuser = usersession['userdict']
        clause_where = ["STATUS=0 AND ART_ID<>'%s'"%article.ART_ID]
        clause_where.append(utils.get_where_clause2(article.ART_KEYWORDS,['ART_KEYWORDS']))
        clause_where = ' and '.join(clause_where) if clause_where else None
        m = connWiki.select("WK_ARTICLES",vars=locals(),where=clause_where,order="MATCH_TIMES DESC",limit=limit).list()
        m = [dict(x, **{ "CREATE_NAME":dictuser.get(x['CREATE_USER'],x['CREATE_USER']), "UPDATE_NAME":dictuser.get(x['UPDATE_USER'],x['UPDATE_USER']), "CAN_MODI":x['CREATE_USER']==usersession['usercode'] }) for x in m]
        return m
    else:
        return []

################################################################################
def get_image(imgid):
    """获取图片"""
    if connWiki:
        m = web.listget(connWiki.select("WK_IMAGES",vars=locals(),where="IMG_ID=$imgid").list(),0,None)
        return m.FILEDATA if m else None
    else:
        return None
def set_image(imgdata,usercode,filename=''):
    """上传图片"""
    if connWiki:
        imgid = hashlib.sha1(imgdata).hexdigest()
        m = web.listget(connWiki.select("WK_IMAGES",vars=locals(),where="IMG_ID=$imgid").list(),0,None)
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

################################################################################
def get_attach(attid):
    """获取附件"""
    if connWiki:
        m = web.listget(connWiki.select("WK_ATTACHS",vars=locals(),where="ATT_ID=$attid").list(),0,None)
        return m.FILEDATA if m else None
    else:
        return None
def set_attach(filedata,usercode,filename=''):
    '''保存附件'''
    if connWiki:
        attid = hashlib.sha1(imgdata).hexdigest()
        m = web.listget(connWiki.select("WK_ATTACHS",vars=locals(),where="ATT_ID=$attid").list(),0,None)
        if not m:
            t = connWiki.transaction()
            try:
                connWiki.insert("WK_ATTACHS",ATT_ID=attid,FILEDATA=base64.encodestring(filedata),FILESIZE=len(filedata),FILENAME=filename,CREATE_USER=usercode,CREATE_TIME=utils.get_currdatetimestr(connWiki.dbtype))
            except Exception, e:
                t.rollback()
                traceback.print_exc()
                return {"ERROR":e}
            else:
                t.commit()
        return {"ATT_ID":attid}
    else:
        return {"ERROR":'No DB!'}

