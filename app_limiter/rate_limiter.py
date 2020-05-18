import ipaddress
import flask
from flask_limiter import Limiter
from datetime import datetime
from functools import wraps
from flask import make_response, render_template

from .models import BlackSubnet
from app_limiter import db


class ExtLimiter(Limiter):
    def limit_and_check(self, limiter, delay=0, limit=0, prefix_subnet='24'):
        def inner(func):

            limiter.limit(self)(func)
            #limit_excess = False
            #time_limit_excess = 0

            @wraps(func)
            def check(*args, **kwargs):
                forwarded_for = flask.request.headers.get('X-Forwarded-For')
                if not forwarded_for:
                    return 'there is not header', 500
                try:
                    net = ipaddress.ip_network(forwarded_for + "/" + prefix_subnet, strict=False)
                except:
                    return 'wrong header', 500
                network_address = str(net.network_address)

                if not limit:
                    return func(*args, **kwargs)
                subnet = BlackSubnet.query.filter_by(subnet=network_address).first()
                if not subnet:
                    added_subnet = BlackSubnet(subnet=network_address)
                    db.session.add(added_subnet)
                    db.session.commit()
                    #add_subnet(subnet)
                    limit_excess = added_subnet.limit_excess
                else:
                    limit_excess = subnet.limit_excess
                if not limit_excess:
                    try:
                        limiter.check()
                    except:
                        subnet.set_time_excess_limit(datetime.now())
                        limit_excess = True
                if limit_excess:
                    time_limit_excess = subnet.time_limit_excess
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
                    #else:
                    #    limit_excess = False
                    #    time_limit_excess = 0
                return func(*args, **kwargs)
            return check
        return inner
