import signal
import sys
from app_limiter import create_app, db
from app_limiter.helpers import exit_gracefully
from app_limiter.models import User

if __name__ == '__main__':
    if len(sys.argv) > 1:
        new_app = create_app(prefix_subnet=sys.argv[1], delay=sys.argv[2], limit=sys.argv[3])
    else:
        new_app = create_app()
    user = User(username="admin")
    user.set_password(password="password")
    db.session.add(user)
    db.session.commit()

    new_app.run(host='0.0.0.0')
    wrap_func = exit_gracefully(new_app)
    signal.signal(signal.SIGINT, wrap_func)
