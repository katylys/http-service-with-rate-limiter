import signal
import sys

from distlib.compat import raw_input

from . import db
from app_limiter.models import User, WhiteSubnet, BlackSubnet


def add_black_subnet(network_address):
    added_subnet = BlackSubnet(subnet=network_address)
    db.session.add(added_subnet)
    db.session.commit()
    return added_subnet


def find_user(username):
    return User.query.filter_by(username=username).first()


def add_user(username, password):
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


def find_white_subnet(subnet):
    return WhiteSubnet.query.filter_by(subnet=subnet).first()


def add_white_subnet(subnet, username):
    added_subnet = WhiteSubnet(who_added_id=username, subnet=subnet)
    db.session.add(added_subnet)
    db.session.commit()


def delete_black_subnet(subnet):
    BlackSubnet.query.filter_by(subnet=subnet).delete()


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


original_sigint = signal.getsignal(signal.SIGINT)


def exit_gracefully(new_app):
    def wrap():
        signal.signal(signal.SIGINT, original_sigint)

        try:
            if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
                db.session.remove()
                db.drop_all()
                sys.exit(1)

        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)

        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, exit_gracefully)
    return wrap()
