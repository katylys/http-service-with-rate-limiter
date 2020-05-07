import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)


class Subnet(db.Model):
    __tablename__ = 'subnets'
    id = db.Column(db.Integer, primary_key=True)
    who_added_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subnet = db.Column(db.String(16), index=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

def init_db():
    db.create_all()

    # Create a test user
    new_user = User('admin', 'password')
    db.session.add(new_user)
    db.session.commit()


if __name__ == '__main__':
    init_db()

