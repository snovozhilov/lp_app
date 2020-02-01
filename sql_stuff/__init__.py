from flask import Flask

from sql_stuff.model import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('sql_config.py')
    db.init_app(app)

    return app