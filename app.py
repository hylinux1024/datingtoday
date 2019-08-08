from flask import Flask

from api import auth, user, config
from models import db

app = Flask(__name__)

app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = config['DATABASE']['uri']

app.secret_key = "8c2c0b555e6e6cb01a5fd36dd981bcee"

db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
