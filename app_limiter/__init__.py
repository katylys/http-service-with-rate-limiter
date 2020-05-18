from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

db = SQLAlchemy()
auth = HTTPBasicAuth()

app = Flask(__name__, template_folder='./templates')


def create_app(prefix_subnet, delay, limit, mode="prod"):
    app.config['LIMIT'] = limit
    app.config['PREFIX_SUBNET'] = prefix_subnet
    app.config['DELAY'] = delay
    app.config['SECRET_KEY'] = 'purring cat'
    if mode == "prod":
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite_test'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        db.create_all()  # Create database tables for our data models

    return app
