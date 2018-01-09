import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # if os.environ.get('DATABASE_URL') is None:
    #     SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    # else:
    #     SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = 'postgres://rfefmneobvwnun:636ab9873720d6bbfb20160a0734aea996b67e4deb20f2cc6efcc5db4418475a@ec2-23-21-246-25.compute-1.amazonaws.com:5432/d9th1fttgij7ql'
    DATABASE_URI = 'postgres://rfefmneobvwnun:636ab9873720d6bbfb20160a0734aea996b67e4deb20f2cc6efcc5db4418475a@ec2-23-21-246-25.compute-1.amazonaws.com:5432/d9th1fttgij7ql'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
