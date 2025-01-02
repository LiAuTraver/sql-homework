from datetime import datetime
import flask
from operations import DatabaseManager
import orm

app = flask.Flask(__name__)
db = DatabaseManager()

app.secret_key = 'your_secret_key'


@app.before_request
def init_db():
    db.connect()


@app.route('/')
def index():
    return flask.redirect(flask.url_for('home'))


@app.route('/home')
def home():
    return flask.render_template('home.html')


@app.route('/home/search', methods=['GET', 'POST'])
def search():
    if flask.request.method == 'POST':
        keyword = flask.request.form.get('keyword', '')
        books = db.search_books(keyword)
        return flask.render_template("search.html", books=books, search=True)
    books=db.search_books('')
    return flask.render_template("search.html",books=books, search=False)


@app.route('/home/add', methods=['GET', 'POST'])
def add_book():
    if flask.request.method == 'POST':
        # 从表单获取数据
        isbn = flask.request.form.get('isbn')
        name = flask.request.form.get('name')
        copies = int(flask.request.form.get('copies'))
        description = flask.request.form.get('description')
        publish_date = flask.request.form.get('publish_date')

        # 创建 Book 实例
        book = orm.Book(isbn=isbn, name=name, copies=copies, available_copies=copies,
                        description=description, publish_date=publish_date)

        success = db.add_book(book)
        if success:
            return flask.redirect(flask.url_for('add_success')) 
        else:
            flask.flash("图书添加失败，请重试。", "error")

    return flask.render_template("add.html")


@app.route('/home/add/success')
def add_success():
    return flask.render_template("add_success.html")


@app.route('/home/delete', methods=['GET', 'POST'])
def delete_book():
    if flask.request.method == 'POST':
        isbn = flask.request.form.get('isbn')  # 获取用户输入的 ISBN
        # 在数据库中查找该 ISBN 的图书
        book = db.get_book_by_isbn(isbn)

        if book:
            # 找到图书，显示图书信息并要求确认删除
            return flask.render_template('delete_confirm.html', book=book)
        else:
            flask.flash("没有找到该图书，删除失败。", "error")
            # 没找到图书，返回当前删除页面
            return flask.redirect(flask.url_for('delete_book'))

    return flask.render_template('delete.html')  # GET 请求时显示删除页面


@app.route('/home/delete/confirm', methods=['POST'])
def confirm_delete():
    isbn = flask.request.form.get('isbn')
    success = db.delete_book(isbn)  # 调用删除方法

    # if success:
    #     flask.flash("图书删除成功！", "success")
    # else:
    #     flask.flash("图书删除失败，请重试。", "error")

    return flask.redirect(flask.url_for('home'))  # 删除成功或失败后跳转到首页


@app.route('/home/edit', methods=['GET', 'POST'])
def edit_book():
    if flask.request.method == 'POST':
        isbn = flask.request.form.get('isbn')  # 获取用户输入的 ISBN
        # 在数据库中查找该 ISBN 的图书
        book = db.get_book_by_isbn(isbn)

        if book:
            # 找到图书，展示图书信息并允许编辑
            return flask.render_template('edit.html', book=book)
        else:
            flask.flash("没有找到该图书，编辑失败。", "error")
            return flask.redirect(flask.url_for('edit_book'))  

    return flask.render_template('edit_search.html')  # GET 请求时显示输入 ISBN 的页面


@app.route('/home/edit/confirm', methods=['POST'])
def confirm_edit():
    isbn = flask.request.form.get('isbn')  
    name = flask.request.form.get('name')  
    description = flask.request.form.get('description')  
    publish_date = flask.request.form.get('publish_date')  

    # 使用原来的 ISBN 来保持唯一性，但不允许修改 ISBN
    new_book = orm.Book(isbn=isbn, name=name, copies=None, available_copies=None,
                        description=description, publish_date=publish_date)

    # 调用更新方法
    success = db.update_book(new_book)

    if success:
        return flask.render_template('edit_success.html')  # 编辑成功后跳转到成功页面
    else:
        flask.flash("图书信息更新失败，请重试。", "error")
        return flask.redirect(flask.url_for('edit_book'))  # 失败则返回编辑页面



if __name__ == '__main__':
    app.run(debug=True)
