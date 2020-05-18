import pytest

from app_limiter import db, app


@pytest.fixture
def client():
    #with create_app(prefix_subnet=24, delay=120, limit="100 per 2 minute", mode="test").test_client() as client:
    #    yield client
    flask_app = app

    flask_app.config['LIMIT'] = "100 per 2 minute"
    flask_app.config['PREFIX_SUBNET'] = 24
    flask_app.config['DELAY'] = 120
    flask_app.config['SECRET_KEY'] = 'purring cat'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite_test'
    flask_app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = flask_app

    db.init_app(flask_app)

    with flask_app.app_context():
        from app_limiter import routes
        db.create_all()  # Create database tables for our data models

    flask_app.config['DEBUG'] = True
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c

def test_ban(client):
    for x in range(100):
        rv = client.get('/', headers={'X-Forwarded-For': '31.31.31.31'})
        assert rv.status_code == 200


