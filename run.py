import sys
from app_limiter import create_app, db
from app_limiter.models import User

if __name__ == '__main__':
    app_l = create_app(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]
    )
    user = User(username="admin")
    user.set_password(password="password")
    db.session.add(user)
    db.session.commit()
    app_l.run(host='0.0.0.0')

