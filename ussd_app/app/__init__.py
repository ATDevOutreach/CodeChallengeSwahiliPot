from config import Config
from flask import Flask
from flask_redis import FlaskRedis

redis = FlaskRedis()


def create_app():
    '''Application factory to initialise and configure the application'''
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    # intialize redis
    redis.init_app(app)

    # register blueprints
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
