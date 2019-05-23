# coding=utf-8
from flask import Flask,request, make_response, jsonify, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_script import Manager
from configure import APP_STATIC_TXT
import os, search, re

app = Flask(__name__)
app.config.from_pyfile('config')
bootstrap = Bootstrap(app)
manager = Manager(app)

# 全文检索
@app.route('/',methods=['GET', 'POST'])
def search_all():
    # GET
    tips =  "<h4>王小波资料检索系统使用说明</h4>"+\
            "<div class=\"text-center\">"+\
                "<b>全文检索：</b>"+\
                "<p>1.在搜索框输入内容，进行全文检索</p>"+\
                "<p>2.该系统具有文本纠错功能，您也可以继续检索原文本</p>"+\
                "<b>文章浏览：</b>"+\
                "<p>1.点击列表中的文章，可以查看文章简介</p>"+\
                "<p>2.点击简介右下方的“阅读原文”，可查看原文</p>"+\
            "</div>"
    tips = "<div style=\"margin-left: 255px;\">"+ \
                        "<h4>使用说明</h4>" + \
                        "<b style=\"margin-top: 20px\">全文检索：</b>"+\
                        "<p>1.在搜索框输入内容，进行全文检索</p>"+\
                        "<p>2.该系统具有文本纠错功能，您也可以继续检索原文本</p>"+\
                        "<b>文章浏览：</b>"+\
                        "<p>1.点击列表中的文章，可以查看文章简介</p>"+\
                        "<p>2.点击简介右下方的“阅读原文”，可查看原文</p>"+\
                    "</div>"
    if request.method == 'GET':
        return render_template('search_all.html', tips=tips)
    # POST
    query = request.form['query']
    query = query.replace(' ', '')
    if not query:
        tips = "请在搜索框输入您想要查询的内容~"
        return render_template('search_all.html', tips=tips)
    in_co = 0
    if query[0] == "【" and query[-1] == "】":
        in_co = 1
        query = query[1:-1]
    show_query = query
    show_co_query = query
    query = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", "", query)
    coquery = query
    if in_co == 0:
        coquery = search.correct_query_api(query)
        show_co_query = search.correct_query_api(show_query)
    wrong = 0
    if query != coquery:
        print(query)
        print(coquery)
        wrong = 1
    # [('寻找无双.txt', [0.27300127206373764, '我不说你就知道，在我们身边有好多人，他们的生活就是编一个故事。不管....']), ...]
    dist = search.search_api(coquery)
    if len(dist) != 0:
        list = []
        id = 1
        for i in dist:
            dict = {}
            dict['id'] = id
            dict['title'] = i[0][0:-4]
            dict['content'] = i[1][1]
            list.append(dict)  # dict中的3个字段与html中定义的变量需一致
            id += 1
        return render_template('search_result.html', books=list, query=show_query, coquery=show_co_query, count=len(dist), wrong=wrong)
    else:
        tips = "很抱歉，未查询到【" + query + "】的相关结果！"
        return render_template('search_all.html', tips=tips)


# 文章浏览
@app.route('/read',methods=['GET', 'POST'])
def read_articles():
    # GET

    introduction = "<div style=\"margin-left: 255px;\">"+ \
                        "<h4>使用说明</h4>" + \
                        "<b style=\"margin-top: 20px\">全文检索：</b>"+\
                        "<p>1.在搜索框输入内容，进行全文检索</p>"+\
                        "<p>2.该系统具有文本纠错功能，您也可以继续检索原文本</p>"+\
                        "<b>文章浏览：</b>"+\
                        "<p>1.点击列表中的文章，可以查看文章简介</p>"+\
                        "<p>2.点击简介右下方的“阅读原文”，可查看原文</p>"+\
                    "</div>"
    to_article = ""
    title = ""
    is_intro = 0
    # POST
    if request.method == 'POST':
        is_intro = 1
        title = request.form['title']
        path = "assets\\books_intro\\" + title + ".txt"
        introduction = ""
        with open(path, encoding='utf-8', errors='ignore') as open_file:
            for line in open_file.readlines():
                introduction += line
        to_article = "阅读原文"
    path = "assets\\books"  # 文件夹目录
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    dist = []
    id = 1
    for file in files:  # 遍历文件夹
        temp = (id, file[0:-4])
        id += 1
        dist.append(temp)
    list = []
    if len(dist) != 0:
        list = []
        for i in dist:
            dict = {}
            dict['id'] = i[0]
            dict['title'] = i[1]
            list.append(dict)
    return render_template('read_articles.html', books=list, introduction=introduction, to_article=to_article, title=title)


#阅读原文
@app.route('/article/<title>')
def article(title):
    file = title + ".txt"
    s = "暂无简介"
    try:
        with open(os.path.join(APP_STATIC_TXT, file), encoding='utf-8') as f:
            s = f.read()
    except IOError:
        print("文章暂未收录！")
    return render_template('article.html', im_title=title, im_content=s)


#404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@manager.command
def dev():
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')  # 监测整个项目所有文件变化。可以加参数，不加就整个项目重加载，加的话就执行方法里的内容。
    live_server.serve(open_url=True)


if __name__ == '__main__':
    manager.run()
