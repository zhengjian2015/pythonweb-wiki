#encoding:utf-8
import web
import model

urls = (
    '/', 'Index'
)

render = web.template.render('templates/')


class Index:
    def GET(self):
		pagedata = {}
		pagedata['datalist'] = model.list_article()
		return render.index(pagedata)

app = web.application(urls, globals())

if __name__ == "__main__":
	app.run()

