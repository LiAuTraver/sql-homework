import asyncio
import os
import sys
import asyncpg
import flask
import flask_material

import operations
import orm

app = flask.Flask(__name__)
flask_material.Material(app)
app.secret_key = os.urandom(24)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        is_valid = loop.run_until_complete(operations.get_connection(username, password))
        if(is_valid):
          print("Login successful")
          flask.redirect(flask.url_for('dashboard'))
        else:
          print("Login failed")
          flask.flash('Invalid username or password','danger')  
    return flask.render_template("login.html")


@app.route('/home')
def home():
    return flask.render_template("home.html")


@app.route('/home/find', methods=['GET', 'POST'])
def find_book():
    if flask.request.method == 'POST':
        pass
    return flask.render_template("find.html")


@app.route('/home/add', methods=['GET', 'POST'])
def add_book():
    if flask.request.method == 'POST':
        pass
    return flask.render_template("add.html")


@app.route('/home/delete', methods=['GET', 'POST'])
def delete_book():
    if flask.request.method == 'POST':
        pass
    return flask.render_template("delete.html")


@app.route('/home/modify', methods=['GET', 'POST'])
def modify_book():
    if flask.request.method == 'POST':
      pass
    return flask.render_template("modify.html")

@app.route("/dashboard")
def dashboard():
    return "Welcome to the Dashboard!"

@app.route('/')
def hello_world():
    return flask.render_template("hello.html", name="Zxs")



async def main():
    conn = await operations.get_connection("postgres", "postgres")
    if conn is None:
        print("Error connecting to the database. the program will now exit.")
        sys.exit(1)
    print("successfully connected to the database")

    students = await operations.fetch_students(conn)
    for student in students:
        print(student)
    _ = await conn.close()


if __name__ == '__main__':
    # asyncio.run(main())
    app.run()
