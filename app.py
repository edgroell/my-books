import os
from datetime import datetime

from flask import Flask, render_template,request, redirect, url_for, flash
from sqlalchemy import desc, asc, or_

from data.data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')
db.init_app(app)

app.config['SECRET_KEY'] = 'a_very_secret_key_that_I_would_change_in_production'

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    search_query = request.args.get('search_query', '').strip()

    sort_columns = {
        'author': Author.name,
        'title': Book.title,
        'publication_year': Book.publication_year
    }

    order_column = sort_columns.get(sort_by, Book.title)

    query = Book.query

    if sort_by == 'author':
        query = query.join(Author)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(or_(Book.title.ilike(search_pattern),
                                 Author.name.ilike(search_pattern)))

    query = query.options(db.joinedload(Book.author))

    if order == 'desc':
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))

    books = query.all()

    return render_template('home.html',
                           books=books,
                           current_sort_by=sort_by,
                           current_order=order,
                           search_query=search_query)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        death_date_str = request.form.get('death_date')

        if not name or not birth_date_str:
            flash('Name and Birth Date are required fields!', 'error')
            return render_template('add_author.html',
                                   name=name,
                                   birth_date=birth_date_str,
                                   death_date=death_date_str)

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Birth Date is invalid! Please use YYY-MM-DD format.', 'error')
            return render_template('add_author.html',
                                   name=name,
                                   birth_date=birth_date_str,
                                   death_date=death_date_str)

        death_date = None
        if death_date_str:
            try:
                death_date = datetime.strptime(death_date_str, '%Y-%m-%d').date()
            except ValueError:
                return render_template('add_author.html',
                                       name=name,
                                       birth_date=birth_date_str,
                                       death_date=death_date_str)

        author = Author(name=name, birth_date=birth_date, death_date=death_date)

        try:
            db.session.add(author)
            db.session.commit()
            flash(f"Author '{name}' added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')
            return render_template('add_author.html',
                                   name=name,
                                   birth_date=birth_date_str,
                                   death_date=death_date_str)

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    template_context = {
        'authors': authors,
        'datetime': datetime
    }

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        publication_year_str = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        template_context['isbn'] = isbn
        template_context['title'] = title
        template_context['publication_year'] = publication_year_str

        if not isbn or not title or not publication_year_str or not author_id:
            flash('All fields are required!', 'error')
            return render_template('add_book.html', **template_context)

        try:
            publication_year = int(publication_year_str)
            if not (1000 <= publication_year <= datetime.now().year + 5):
                flash('Publication Year seems unrealistic. Please check.', 'error')
                return render_template('add_book.html', **template_context)
        except ValueError:
            flash('Publication Year must be a valid number!', 'error')
            return render_template('add_book.html', **template_context)

        try:
            author_id = int(author_id)
            existing_author = Author.query.get(author_id)
            if not existing_author:
                flash('Selected Author does not exist!', 'error')
                return render_template('add_book.html', **template_context)
        except ValueError:
            flash('Invalid Author selection!', 'error')
            return render_template('add_book.html', **template_context)

        book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)

        try:
            db.session.add(book)
            db.session.commit()
            flash(f"Book '{title}' added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')
            return render_template('add_book.html', **template_context)

    return render_template('add_book.html', **template_context)


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            db.session.delete(book)
            db.session.commit()
            flash(f"Book '{book.title}' by {book.author.name if book.author else 'Unknown Author'} deleted successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting the book: {e}', 'error')
            return redirect(url_for('index'))
    else:
        return render_template('delete_confirm.html', book=book)


if __name__ == '__main__':
    # with app.app_context():
    #   db.create_all()
    app.run(debug=True)
