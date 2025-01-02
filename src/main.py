from datetime import datetime
import flask
from operations import DatabaseManager
import orm

app = flask.Flask(__name__)
db = DatabaseManager()

@app.before_request
def init_db():
    db.connect()
    # print("Database connected")

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
    return flask.render_template("search.html", search=False)


@app.route('/home/add', methods=['GET', 'POST'])
def add_book():
    if flask.request.method == 'POST':
        isbn = flask.request.form.get('isbn')
        name = flask.request.form.get('name')
        copies = int(flask.request.form.get('copies'))
        available_copies = int(flask.request.form.get('available_copies'))
        description = flask.request.form.get('description')
        publish_date = flask.request.form.get('publish_date')

        publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').date() if publish_date else None
        
        book = orm.Book(isbn=isbn, name=name, copies=copies, available_copies=available_copies, description=description, publish_date=publish_date)
        success = db.add_book(book)
        if success:
            flask.flash('Book added successfully!')
        else:
            flask.flash('Failed to add book.')

    return flask.render_template('add.html')

@app.route('/home/delete', methods=['GET', 'POST'])
def delete_book():
    if flask.request.method == 'POST':
        isbn = flask.request.form.get('isbn')
        success = db.delete_book(isbn)
        if success:
            flask.flash('Book deleted successfully!')
        else:
            flask.flash('Failed to delete book.')

    return flask.render_template('delete.html')

@app.route('/home/edit', methods=['GET', 'POST'])
def edit_book():
    if flask.request.method == 'POST':
        isbn = flask.request.form.get('isbn')
        name = flask.request.form.get('name')
        copies = int(flask.request.form.get('copies'))
        available_copies = int(flask.request.form.get('available_copies'))
        description = flask.request.form.get('description')
        publish_date = flask.request.form.get('publish_date')

        publish_date = datetime.datetime.strptime(publish_date, '%Y-%m-%d').date() if publish_date else None
        
        book = orm.Book(isbn=isbn, name=name, copies=copies, available_copies=available_copies, description=description, publish_date=publish_date)
        success = db.update_book(book)
        if success:
            flask.flash('Book updated successfully!')
        else:
            flask.flash('Failed to update book.')

    return flask.render_template('edit.html')

if __name__ == '__main__':
    app.run(debug=True)
