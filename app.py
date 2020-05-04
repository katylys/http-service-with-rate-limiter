import argparse
import ipaddress
import socket
import struct
import sys
from functools import wraps
from flask import Flask, request, make_response, render_template
from flask_limiter import Limiter
import time


class ExtLimiter(Limiter):
    def limit_and_check(self, limiter, delay=0, limit=0):
        def inner(func):
            limiter.limit(self)(func)
            flag = 1  # rate limit не превышен
            start = 0
            @wraps(func)
            def check(*args, **kwargs):
                if not limit:
                    return func(*args, **kwargs)
                nonlocal flag
                nonlocal start
                if flag:
                    try:
                        limiter.check()
                    except:
                        start = time.time()
                        flag = 0
                if not flag:
                    diff = time.time() - start
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
                        flag = 1
                        start = 0
                return func(*args, **kwargs)
            return check
        return inner


def get_subnet(subnet):
    def inner():
        net = ipaddress.ip_network(request.remote_addr + "/" + subnet, strict=False)
        return str(net.network_address)
    return inner


def main(limit, prefix_subnet, delay):
    mask = (1 << 32) - (1 << 32 >> int(prefix_subnet))
    mask_subnet = socket.inet_ntoa(struct.pack(">L", mask))
    app = Flask(__name__, template_folder='./templates')
    limiter = ExtLimiter(app, default_limits=[limit], key_func=get_subnet(mask_subnet), strategy="moving-window")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    @limiter.limit_and_check(limiter, delay=int(delay), limit=limit)
    def index(path):
        resp = make_response(render_template('index.html'), 200)
        return resp
    app.run(debug=True)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--limit', default=0)
    parser.add_argument('-p', '--prefix_subnet')
    parser.add_argument('-d', '--delay')

    return parser


if __name__ == "__main__":
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    main(namespace.limit, namespace.prefix_subnet, namespace.delay)
