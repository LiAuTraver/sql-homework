from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 处理登录逻辑
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/home/find', methods=['GET', 'POST'])
def find_book():
    if request.method == 'POST':
        # 处理查找图书逻辑
        pass
    return render_template("find.html")

@app.route('/home/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # 处理增加图书逻辑
        pass
    return render_template("add.html")

@app.route('/home/delete', methods=['GET', 'POST'])
def delete_book():
    if request.method == 'POST':
        # 处理删除图书逻辑
        pass
    return render_template("delete.html")

@app.route('/home/modify', methods=['GET', 'POST'])
def modify_book():
    if request.method == 'POST':
        # 处理更改图书信息逻辑
        pass
    return render_template("modify.html")

@app.route('/')
def hello_world():
    return render_template("hello.html",name="Zxs")
 
if __name__ == '__main__':
    app.run()
