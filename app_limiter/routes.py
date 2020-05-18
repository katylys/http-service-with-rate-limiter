from flask import app as g, request, make_response, render_template, jsonify
from app_limiter import auth
from app_limiter.rate_limiter import ExtLimiter, get_subnet
from .helpers import find_user, add_user, add_white_subnet, delete_black_subnet, find_white_subnet
from flask import current_app as app


limitation = [] if not app.config.get('LIMIT') else [app.config.get('LIMIT')]
limiter = ExtLimiter(app,
                     default_limits=limitation,
                     key_func=get_subnet(app.config.get('PREFIX_SUBNET')),
                     strategy="moving-window")


@auth.verify_password
def verify_password(username, password):
    user = find_user(username)
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/new_user', methods=['POST'])
@auth.login_required
def new_user():
    if not g.user.username == "admin":
        return 'not allowed!', 401
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'not credentials!', 500
    user_exist = find_user(username)
    if user_exist:
        return 'wrong credentials!', 409
    add_user(username, password)
    return jsonify({'username': username}), 201


@app.route('/white_list_subnet', methods=['POST'])
@auth.login_required
def white_list_subnet():
    subnet = request.json.get('subnet')
    found_subnet = find_white_subnet(subnet)
    if not found_subnet:
        add_white_subnet(subnet, g.user.username)
        delete_black_subnet(subnet)

    resp = make_response(render_template('index.html'), 200)
    return resp


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@limiter.limit_and_check(limiter,
                         delay=int(app.config.get('DELAY')),
                         limit=app.config.get('LIMIT'),
                         prefix_subnet=app.config.get('PREFIX_SUBNET'))
def index(path):
    resp = make_response(render_template('index.html'), 200)
    return resp
