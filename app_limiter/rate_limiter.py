import flask
from flask_limiter import Limiter
from datetime import datetime
from functools import wraps
from flask import make_response, render_template
from app_limiter.helpers import add_black_subnet
from .models import BlackSubnet, WhiteSubnet
import ipaddress
import socket
import struct
from flask import request


class ExtLimiter(Limiter):
    def limit_and_check(self, limiter, delay=0, limit=0, prefix_subnet='24'):
        def inner(func):
            if not limit:
                return func

            limiter.limit(self)(func)

            @wraps(func)
            def check(*args, **kwargs):
                forwarded_for = flask.request.headers.get('X-Forwarded-For')
                if not forwarded_for:
                    return 'there is not header', 400
                try:
                    net = ipaddress.ip_network(forwarded_for + "/" + prefix_subnet, strict=False)
                except:
                    return 'wrong header', 400
                network_address = str(net.network_address)
                black_subnet = BlackSubnet.query.filter_by(subnet=network_address).first()
                white_subnet = WhiteSubnet.query.filter_by(subnet=network_address).first()
                if white_subnet:
                    return func(*args, **kwargs)
                if not black_subnet:
                    added_subnet = add_black_subnet(network_address)
                    limit_excess = added_subnet.limit_excess
                else:
                    limit_excess = black_subnet.limit_excess
                if not limit_excess:
                    try:
                        limiter.check()
                    except IndexError:
                        black_subnet.set_time_excess_limit(datetime.now())
                        limit_excess = True
                if limit_excess:
                    time_limit_excess = black_subnet.time_limit_excess
                    diff = (datetime.now() - time_limit_excess).total_seconds()
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
                return func(*args, **kwargs)

            return check

        return inner


def get_subnet(prefix_subnet):
    if not prefix_subnet:
        return None

    def inner():
        mask = (1 << 32) - (1 << 32 >> int(prefix_subnet))
        mask_subnet = socket.inet_ntoa(struct.pack(">L", mask))
        fo = request.headers.get('X-Forwarded-For')
        if not fo:
            return 'wrong header', 400
        net = ipaddress.ip_network(fo + "/" + mask_subnet, strict=False)
        network_address = str(net.network_address)
        found_subnet = WhiteSubnet.query.filter_by(subnet=network_address).first()
        result_inner = None if found_subnet else network_address
        return result_inner

    return inner
