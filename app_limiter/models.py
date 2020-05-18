import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import ipaddress
import socket
import struct
from flask import request
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

    #def __init__(self, subnet, who_added_id):
    #    self.who_added_id = who_added_id
    #    self.subnet = subnet


def find_user(username):
    return User.query.filter_by(username=username).first()


def add_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()


def find_subnet(subnet):
    d = WhiteSubnet.query.filter_by(subnet=subnet).first()
    if d:
        return d.first()
    return None


def add_subnet(subnet, username=None):
    added_subnet = WhiteSubnet(who_added_id=username, subnet=subnet)
    db.session.add(added_subnet)
    db.session.commit()


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


def get_subnet(prefix_subnet):
    def inner():
        mask = (1 << 32) - (1 << 32 >> int(prefix_subnet))
        mask_subnet = socket.inet_ntoa(struct.pack(">L", mask))
        fo = request.headers.get('X-Forwarded-For')
        if not fo:
            return 'wrong header', 500
        net = ipaddress.ip_network(fo + "/" + mask_subnet, strict=False)
        network_address = str(net.network_address)
        found_subnet = WhiteSubnet.query.filter_by(subnet=network_address).first()#find_subnet(network_address)
        result_inner = None if found_subnet else network_address
        return result_inner

    return inner
