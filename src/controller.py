import datetime
import functools
import os
import typing
import flask
import flask_material  # type: ignore
import operations
import orm

app: flask.Flask
database_manager: operations.DatabaseManager

app = flask.Flask(__name__)
flask_material.Material(app)
app.secret_key = os.urandom(24)
database_manager = operations.DatabaseManager()


def login_required(func):
    """
    Decorator to check if user is logged in.
    """
    @functools.wraps(func)
    def decorate_me(*args, **kwargs):
        if "user" not in flask.session:
            flask.flash("Unauthorized access. Please login first.", "error")
            return flask.redirect(flask.url_for("login"))
        return func(*args, **kwargs)
    return decorate_me

# @app.before_request
# def init_db():
#     database_manager.connect()

@app.route("/")
def index():
    return flask.render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  if flask.request.method == 'POST':
    database_manager.db_params["user"] = flask.request.form["username"]
    database_manager.db_params["password"] = flask.request.form["password"]
    try:
      database_manager.connect()
      flask.session['user'] = flask.request.form["username"]
      return flask.redirect(flask.url_for("home"))
    except Exception as e:
      flask.session.pop("user", None)
      # flask.flash(f"Login failed. Please check your username and password. Error: {str(e)}", "error")
  else:
    flask.session.pop("user", None)
  return flask.render_template("login.html")


@app.route("/home")
@login_required
def home():
    return flask.render_template("home.html")


@app.route("/home/search", methods=["GET", "POST"])
@login_required
def search():
    if flask.request.method == "POST":
        keyword = flask.request.form.get("keyword", "")
        books = database_manager.search_books(keyword)
        return flask.render_template("search/search.html", books=books, search=True)
    books = database_manager.search_books("")
    return flask.render_template("search/search.html", books=books, search=False)


@app.route("/home/add", methods=["GET", "POST"])
@login_required
def add_book():
    if flask.request.method == "POST":
        # 从表单获取数据
        isbn = typing.cast(str, flask.request.form.get("isbn"))
        name = typing.cast(str, flask.request.form.get("name"))
        copies = typing.cast(int, flask.request.form.get("copies"))
        description = flask.request.form.get("description")
        publish_date = typing.cast(
            datetime.datetime, flask.request.form.get("publish_date")
        )

        # 创建 Book 实例
        book = orm.Book(
            isbn=isbn,
            name=name,
            copies=copies,
            available_copies=copies,
            description=description,
            publish_date=publish_date,
        )

        success = database_manager.add_book(book)
        if success:
            return flask.redirect(flask.url_for("add_success"))
        else:
            flask.flash("图书添加失败，请重试。", "error")

    return flask.render_template("add/add.html")


@app.route("/home/add/success")
@login_required
def add_success():
    return flask.render_template("add/add_success.html")


@app.route("/home/delete", methods=["GET", "POST"])
@login_required
def delete_book():
    if flask.request.method == "POST":
        isbn = typing.cast(str, flask.request.form.get("isbn"))  # 获取用户输入的 ISBN
        # 在数据库中查找该 ISBN 的图书
        book = database_manager.get_book_by_isbn(isbn)

        if book:
            # 找到图书，显示图书信息并要求确认删除
            return flask.render_template("delete/delete_confirm.html", book=book)
        else:
            flask.flash("没有找到该图书，删除失败。", "error")
            # 没找到图书，返回当前删除页面
            return flask.redirect(flask.url_for("delete_book"))

    return flask.render_template("delete/delete.html")  # GET 请求时显示删除页面


@app.route("/home/delete/confirm", methods=["POST"])
@login_required
def confirm_delete():
    isbn = typing.cast(str, flask.request.form.get("isbn"))
    success = database_manager.delete_book(isbn)  # 调用删除方法

    # if success:
    #     flask.flash("图书删除成功！", "success")
    # else:
    #     flask.flash("图书删除失败，请重试。", "error")

    return flask.redirect(flask.url_for("home"))  # 删除成功或失败后跳转到首页


@app.route("/home/edit", methods=["GET", "POST"])
@login_required
def edit_book():
    if flask.request.method == "POST":
        isbn = typing.cast(str, flask.request.form.get("isbn"))  # 获取用户输入的 ISBN
        # 在数据库中查找该 ISBN 的图书
        book = database_manager.get_book_by_isbn(isbn)

        if book:
            # 找到图书，展示图书信息并允许编辑
            return flask.render_template("edit/edit.html", book=book)
        else:
            flask.flash("没有找到该图书，编辑失败。", "error")
            return flask.redirect(flask.url_for("edit_book"))

    return flask.render_template(
        "edit/edit_search.html"
    )  # GET 请求时显示输入 ISBN 的页面


@app.route("/home/edit/confirm", methods=["POST"])
@login_required
def confirm_edit():
    isbn = typing.cast(str, flask.request.form.get("isbn"))
    name = typing.cast(str, flask.request.form.get("name"))
    description = typing.cast(str, flask.request.form.get("description"))
    publish_date = typing.cast(
        datetime.datetime, flask.request.form.get("publish_date")
    )

    # 使用原来的 ISBN 来保持唯一性，但不允许修改 ISBN
    new_book = orm.Book(
        isbn=isbn,
        name=name,
        copies=None,  # type: ignore
        available_copies=None,  # type: ignore
        description=description,
        publish_date=publish_date,
    )

    # 调用更新方法
    success = database_manager.update_book(new_book)

    if success:
        return flask.render_template(
            "edit/edit_success.html"
        )  # 编辑成功后跳转到成功页面
    else:
        flask.flash("图书信息更新失败，请重试。", "error")
        return flask.redirect(flask.url_for("edit/edit_book"))  # 失败则返回编辑页面

if __name__ == "__main__":
    raise Exception("don't run me! I am angry now!")
else:
    pass