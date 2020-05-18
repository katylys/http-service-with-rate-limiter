import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(64))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


class BlackSubnet(db.Model):
    __tablename__ = 'black_subnets'
    id = db.Column(db.Integer, primary_key=True)
    subnet = db.Column(db.String(16), index=True, unique=True)
    limit_excess = db.Column(db.Boolean, default=False)
    time_limit_excess = db.Column(db.DateTime, default=None)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

    def set_time_excess_limit(self, time):
        self.time_limit_excess = time
        self.limit_excess = True


class WhiteSubnet(db.Model):
    __tablename__ = 'white_subnets'
    id = db.Column(db.Integer, primary_key=True)
    who_added_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subnet = db.Column(db.String(16), index=True, unique=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())