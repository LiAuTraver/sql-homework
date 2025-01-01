import asyncio
import sys
import asyncpg
import flask
import flask_material

import src.operations
from src import orm

app = flask.Flask(__name__)
flask_material.Material(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        return flask.redirect(flask.url_for('home'))
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


@app.route('/')
def hello_world():
    return flask.render_template("hello.html", name="Zxs")


async def get_connection() -> asyncpg.connect:
    try:
        conn = await asyncpg.connect(**orm.db_params)
        version = await conn.fetchval("SELECT version();")
        print("Connected to the database, version: ", version)
        return conn
    except Exception as e:
        print("Error connecting to the database")
        print(e)
        return None


async def main():
    conn = await get_connection()
    if conn is None:
        print("Error connecting to the database. the program will now exit.")
        sys.exit(1)
    print("successfully connected to the database")
    print("successfully closed the connection")

    students = await src.operations.fetch_students(conn)
    for student in students:
        print(student)
    _ = await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
    app.run()
