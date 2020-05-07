import argparse
import ipaddress
import os
import socket
import struct
import sys
from functools import wraps
from flask import request, make_response, render_template, jsonify, g, abort
from flask_limiter import Limiter
import time

from app import app, auth, db
from app.models import User, Subnet


class ExtLimiter(Limiter):
    def limit_and_check(self, limiter, delay=0, limit=0):
        def inner(func):
            limiter.limit(self)(func)
            limit_excess = False
            time_limit_excess = 0

            @wraps(func)
            def check(*args, **kwargs):
                if not limit:
                    return func(*args, **kwargs)
                nonlocal limit_excess
                nonlocal time_limit_excess
                if not limit_excess:
                    try:
                        limiter.check()
                    except:
                        time_limit_excess = time.time()
                        limit_excess = True
                if limit_excess:
                    diff = time.time() - time_limit_excess
                    if diff < delay:
                        pieces = limit.split(" ")
                        number_requests = pieces[0]
                        end_req = "" if number_requests == "1" else "s"
                        req = "request" + end_req
                        pieces.insert(1, req)
                        paste_limit = " ".join(pieces)
                        resp = make_response(render_template('429.html', LIMIT=paste_limit), 429)
                        resp.headers['Content-Type'] = 'text/html'
                        resp.headers['Retry-After'] = delay - int(diff)
                        return resp
                    else:
                        limit_excess = False
                        time_limit_excess = 0
                return func(*args, **kwargs)

            return check

        return inner


def get_subnet(prefix_subnet):
    def inner():
        mask = (1 << 32) - (1 << 32 >> int(prefix_subnet))
        mask_subnet = socket.inet_ntoa(struct.pack(">L", mask))
        net = ipaddress.ip_network(request.remote_addr + "/" + mask_subnet, strict=False)
        network_address = str(net.network_address)
        found_subnet = db.session.query(Subnet).filter(Subnet.subnet == network_address).first()
        result_inner = None if found_subnet else network_address
        return result_inner

    return inner


def main(limit, prefix_subnet, delay):
    limitation = [] if limit == '0' else [limit]
    limiter = ExtLimiter(app, default_limits=limitation, key_func=get_subnet(prefix_subnet), strategy="moving-window")

    @auth.verify_password
    def verify_password(username_or_token, password):
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
        g.user = user
        return True

    @app.route('/change_password', methods=['POST'])
    @auth.login_required
    def change_password():
        password = request.json.get('password')
        repeated_password = request.json.get('repeated_password')

        if password != repeated_password:
            abort(400)
        user = User(username=g.user.username)
        user.modify(password=password)
        user.save()
        return jsonify({'username': user.username}), 201

    @app.route('/new_user', methods=['POST'])
    @auth.login_required
    def new_user():
        if not g.user.username == "admin":
            abort(400)
        u = request.json
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            abort(400)
        user_exist = db.session.query(User).filter(User.username == username).first()
        if user_exist:
            sys.exit("Existing user!")
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'username': user.username}), 201

    @app.route('/white_list_subnet', methods=['POST'])
    @auth.login_required
    def white_list_subnet():
        subnet = request.json.get('subnet')
        found_subnet = db.session.query(Subnet).filter(Subnet.subnet == subnet).first()
        if not found_subnet:
            added_subnet = Subnet(who_added_id=g.user.username, subnet=subnet)
            db.session.add(added_subnet)
            db.session.commit()
        resp = make_response(render_template('index.html'), 200)
        return resp

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    @limiter.limit_and_check(limiter, delay=int(delay), limit=limit)  # , key_func=get_subnet(prefix_subnet)
    def index(path):
        resp = make_response(render_template('index.html'), 200)
        return resp

    if not os.path.exists('db.sqlite'):
        db.create_all()
    #db.drop_all()
    user = User(username="admin", password="password")
    db.session.add(user)
    db.session.commit()
    app.run(debug=True, host='0.0.0.0')


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--limit', default="100 per minute")
    parser.add_argument('-p', '--prefix_subnet', default=24)
    parser.add_argument('-d', '--delay', default=120)

    return parser


if __name__ == "__main__":
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    main(namespace.limit, namespace.prefix_subnet, namespace.delay)

#curl -u abc:abc -i -X POST -H "Content-Type: application/json" -d "{\"subnet\":\"127.0.0.0\"}" http://127.0.0.1:5000/white_list_subnet
#curl -i -H "Content-Type: application/json" -X POST -d "{\"username\":\"abc\", \"password\":\"abc\"}" 127.0.0.1:5000/new_user
