# -*-coding:utf-8-*-
"""Configuration file"""

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))  # base directory

# load dotenv file
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)
print(dotenv_path)


class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET', 'my secret key')

    REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")

    AT_SENDER_ID = os.environ.get("AT_SENDER_ID")
    AT_PRODUCT_NAME = os.environ.get("AT_PRODUCT_NAME")
    AT_PROVIDER_CHANNEL = os.environ.get("AT_PROVIDER_CHANNEL")

    @classmethod
    def init_app(cls, app):
        """Class method"""
        import logging
        from logging import getLogger
        from logging.handlers import SysLogHandler

        # log warnings to std input
        sys_handler = SysLogHandler()
        sys_handler.setFormatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        sys_handler.setLevel(logging.INFO)
        # add handlers to loggers
        loggers = [app.logger, getLogger('gunicorn')]
        for logger in loggers:
            logger.addHandler(sys_handler)
