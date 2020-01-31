from flask import Flask

from model import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('tg_config.py')
    db.init_app(app)

    return app