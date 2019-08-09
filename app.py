from flask import Flask

from api import auth, users, config, make_response_error
from models import db

app = Flask(__name__)

app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = config['DATABASE']['uri']

app.secret_key = "8c2c0b555e6e6cb01a5fd36dd981bcee"

db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.errorhandler(404)
def not_found_error(error):
    return make_response_error(404, error.description)


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return make_response_error(500, error.description)


if __name__ == '__main__':
    app.run()
