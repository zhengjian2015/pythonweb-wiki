#encoding:utf-8
from config import * 

urls = ("","Index","/", "Index",
        "/rst/arts",    "ListArticle",
        "/rst/img",     "Image",
        "/rst/art",  "Article",
	   "/.*",     "viewController")


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
        web.debug(render)
        if render:
            ctxdata = get_ctx()
            pagedata = {}
            web.debug(web.ctx.path)
            web.debug("22222222222222222222222222222222")
            if web.ctx.path.startswith('/wklist'):
                #views里面要有wklist,否则进不来
                pagedata['datalist'],pagedata['datasize'] = mwiki.list_article(param)
                #wklist页面里嵌套wkside页面
                pageside = get_modulerender('wiki/views/wkside')
                pagedata['sidepage'] = pageside
                web.debug(pageside)
                web.debug(param)
                #前端好强大啊，引入blog.css前后完全不一样了。。。。。。。
                return platLayout(render(ctxdata,param,pagedata),nobars=True,title='文章列表',
                                  addcss=['/static/css/pages/blog.css'])
            elif web.ctx.path.startswith('/wkv2'):
                pageside = get_modulerender('wiki/views/wkside')
                web.debug("??"*30)
                pagedata['sidepage'] = pageside
                pagedata['artldata'] = mwiki.get_article(param.get('id',''))
                if pagedata['artldata']:
                    #pagedata['relateart'] = mwiki.list_relarticle(pagedata['artldata'])
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
                artid = param.get('id','')
                pagedata['article'] = mwiki.get_article(artid) if artid else {}
            return render(ctxdata,param,pagedata)



class ListArticle(baseServiceController):
    def GET(self):
        '''文章列表'''
        param = web.input()
        retval = mwiki.list_article(param)
        return formatting.json_string(retval[0])



class Article(baseServiceController):
    def POST(self):
        '''保存文章内容'''
        web.debug("xxx"*30)
        param = web.input()
        web.debug(param)
        baseServiceController.POST(self,param)
        ctxdata = get_ctx()
        usercode = ctxdata['usersession']['usercode']
        retval = mwiki.set_article(param,usercode)
        return formatting.json_string(retval)

class Image(baseServiceController):
    def GET(self):
        param = web.input(id='')
        web.debug(param)
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
        web.debug("**44"*30)
        web.debug(param)    
        baseServiceController.POST(self,param)
        retmsg = {"success":1, "message":"上传成功", "url":"图片地址"}
        if param.has_key("editormd_image_file"):
            ctxdata = get_ctx()
            usercode = ctxdata['usersession']['usercode']
            retval = mwiki.set_image(param['editormd_image_file'].value,usercode,param['editormd_image_file'].filename)
            if retval.has_key("ERROR"):
                retmsg['success'] = 0
                retmsg['message'] = retval['ERROR']
            else:
                retmsg['url'] = ctxdata.get('realhome','')+'/x/wiki/rst/img?id='+retval['IMG_ID']
        else:
            retmsg['success'] = 0
            retmsg['message'] =  u"上传图标数据为空！"
        return formatting.json_string(retmsg)
