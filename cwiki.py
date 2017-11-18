#encoding:utf-8

from config import *

urls = ("","Index","/", "Index",
    "/rst/arts",        "ListArticle",
    "/rst/art",         "Article",
    "/rst/img",         "Image",
    "/rst/att",         "Attachment",
    "/rst/modiusers",   "SetModiUsers",
    "/.*",              "viewController")
module_urls = web.application(urls, locals())

import mwiki

class Index:
    def GET(self):
        return web.seeother('/wklist')

class viewController(baseViewController):
    def GET(self):
        baseViewController.GET(self)
        param = web.input()
        render = get_modulerender('wiki/views'+web.ctx.path)
        if render:
            ctxdata = get_ctx()
            pagedata = {}
            if web.ctx.path.startswith('/wklist'):
                #views里面要有wklist,否则进不来
                pagedata['datalist'],pagedata['datasize'] = mwiki.list_article(param)
                #wklist页面里嵌套wkside页面
                pageside = get_modulerender('wiki/views/wkside')
                pagedata['sidepage'] = pageside
                pagedata['keywords'] = mwiki.get_allkeywords()
                pagedata['hotart'] = mwiki.list_hotarticle()
                #前端好强大啊，引入blog.css前后完全不一样了。。。。。。。
                return platLayout(render(ctxdata,param,pagedata),nobars=True,title='文章列表',
                                  addcss=['/static/css/pages/blog.css'])
            elif web.ctx.path.startswith('/wkv2'):
                pageside = get_modulerender('wiki/views/wkside')
                pagedata['sidepage'] = pageside
                pagedata['keywords'] = mwiki.get_allkeywords()
                pagedata['artldata'] = mwiki.get_article(param.get('id',''))
                if pagedata['artldata']:
                    pagedata['relateart'] = mwiki.list_relarticle(pagedata['artldata'])
                    mwiki.increase_readcount(param.get('id',''))
                return platLayout(render(ctxdata,param,pagedata),nobars=True,title=pagedata['artldata'].get('ART_TITLE','查看文章'),
                                  addcss=['/static/css/pages/blog.css','/x/wiki/static/css/style.css','/x/wiki/static/css/editormd.preview.min.css'],
                                  addjs =['/x/wiki/static/lib/marked.min.js',
                                          '/x/wiki/static/lib/prettify.min.js',
                                          '/x/wiki/static/lib/raphael.min.js',
                                          '/x/wiki/static/lib/underscore.min.js',
                                          '/x/wiki/static/lib/sequence-diagram.min.js',
                                          '/x/wiki/static/lib/flowchart.min.js',
                                          '/x/wiki/static/lib/jquery.flowchart.min.js',
                                          '/x/wiki/static/editormd.min.js'])
            elif web.ctx.path.startswith('/wkedit'):
                #编辑需要判断登录状态、操作员权限
                baseViewController.GET(self)
                artid = param.get('id','')
                pagedata['article'] = mwiki.get_article(artid) if artid else {}
                if pagedata['article']:
                    if pagedata['article'].get('CREATE_USER','')!=ctxdata['usersession']['usercode'] and pagedata['article'].get('CANMODI_USERS','').find(ctxdata['usersession']['usercode'])<0:
                        raise custom_error.internalerror('你没有权限编辑这篇文章：%s'%pagedata['article'].get('ART_TITLE',''))
            return render(ctxdata,param,pagedata)
        else:
            raise custom_error.notfound(web.ctx.path)

class ListArticle(baseServiceController):
    def GET(self):
        '''文章列表'''
        param = web.input()
        retval = mwiki.list_article(param)
        return formatting.json_string(retval[0])

class Article(baseServiceController):
    def GET(self):
        '''取文章内容'''
        param = web.input(id='')
        if param.id:
            retval = mwiki.get_article(param.id)
        else:
            retval = {}
        return formatting.json_string(retval)
    def POST(self):
        '''保存文章内容'''
        param = web.input()
        baseServiceController.POST(self,param)
        ctxdata = get_ctx()
        usercode = ctxdata['usersession']['usercode']
        retval = mwiki.set_article(param,usercode)
        return formatting.json_string(retval)
    def DELETE(self):
        '''删除文章'''
        param = web.input()
        baseServiceController.POST(self,param)
        artid = param.get('id','')
        article = mwiki.get_article(artid) if artid else {}
        if article:
            ctxdata = get_ctx()
            if article.get('CREATE_USER','')!=ctxdata['usersession']['usercode']:
                retval = {'ERROR':'你没有权限编辑这篇文章：%s'%article.get('ART_TITLE','')}
            else:
                artldata = {'ART_ID':artid,'STATUS':1}
                retval = mwiki.set_article(artldata,ctxdata['usersession']['usercode'])
                if not retval.has_key('ERROR'):
                    retval = {'SUCCESS':'删除成功！'}
        else:
            retval = {'ERROR':'文章不存在！'}
        return formatting.json_string(retval)

class Image(baseServiceController):
    """图片内容获取与上传"""
    def GET(self):
        param = web.input(id='')
        imgdata = mwiki.get_image(param.id) if param.id else None
        if imgdata:
            if param.get('t','')=='base64':
                return imgdata
            else:
                web.header('Content-Type', 'image/png')
                return base64.decodestring(imgdata)
        else:
            return ''
    def POST(self):
        '''用于给Editor.md上传图片用'''
        param = web.input(editormd_image_file={})
        baseServiceController.POST(self,param)
        retmsg = {"success":1, "message":"上传成功", "url":"图片地址"}
        if param.has_key('editormd_image_file'):
            ctxdata = get_ctx()
            usercode = ctxdata['usersession']['usercode']
            retval = mwiki.set_image(param['editormd_image_file'].value,usercode,param['editormd_image_file'].filename)
            if retval.has_key('ERROR'):
                retmsg['success'] = 0
                retmsg['message'] = retval['ERROR']
            else:
                retmsg['url'] = ctxdata.get('realhome','')+'/x/wiki/rst/img?id='+retval['IMG_ID']
        else:
            retmsg['success'] = 0
            retmsg['message'] = u"上传图标数据为空！"
        return formatting.json_string(retmsg)

class Attachment(baseServiceController):
    """附件内容获取与上传"""
    def GET(self):
        param = web.input(id='')
        imgdata = mwiki.get_attach(param.id) if param.id else None
        if imgdata:
            if param.get('t','')=='base64':
                return imgdata
            else:
                web.header('Content-Type', 'image/png')
                return base64.decodestring(imgdata)
        else:
            return ''
    def POST(self):
        '''用于给Editor.md上传图片用'''
        param = web.input(editormd_image_file={})
        baseServiceController.POST(self,param)
        retmsg = {"success":1, "message":"上传成功", "url":"图片地址"}
        if param.has_key('editormd_image_file'):
            ctxdata = get_ctx()
            usercode = ctxdata['usersession']['usercode']
            retval = mwiki.set_image(param['editormd_image_file'].value,usercode,param['editormd_image_file'].filename)
            if retval.has_key('ERROR'):
                retmsg['success'] = 0
                retmsg['message'] = retval['ERROR']
            else:
                retmsg['url'] = ctxdata.get('realhome','')+'/x/wiki/rst/img?id='+retval['IMG_ID']
        else:
            retmsg['success'] = 0
            retmsg['message'] = u"上传图标数据为空！"
        return formatting.json_string(retmsg)

class SetModiUsers(baseServiceController):
    def GET(self):
        '''取文章可修改用户'''
        param = web.input(ART_ID='')
        m = mwiki.get_article(param.ART_ID)
        if not m:
            return ''
        elif m and m.has_key('ERROR'):
            return  ''
        elif m:
            return m.CANMODI_USERS
    def POST(self):
        '''设置文章可修改用户'''
        param = web.input(ART_ID='',canmodiusers='')
        utils.debug(param)
        baseServiceController.POST(self,param)
        retval = mwiki.modi_users(param.ART_ID,param.canmodiusers)
        if retval.has_key('ERROR'):
            return retval['ERROR']
        else:
            return '设置成功'
