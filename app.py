import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data.data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')
db.init_app(app)

# with app.app_context():
#   db.create_all()

# if __name__ == '__main__':
#     app.run(debug=True)
