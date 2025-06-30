from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)
    def __repr__(self):
        return f"<Author(id='{self.id}', name='{self.name}')>"
    def __str__(self):
        return f"<Author(name='{self.name}', birth_date='{self.birth_date}')>"

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', backref='books')
    def __repr__(self):
        return f"<Book(id='{self.id}', isbn='{self.isbn}', title='{self.title}')>"
    def __str__(self):
        author_name = self.author.name if self.author else "Unknown Author"
        return f"<Book(title='{self.title}', author='{author_name}', publication_year='{self.publication_year}')>"


