
"""
    config.py
    - settings for the flask application object
"""

class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://crisismgmt:crisismgmt.c1e5gxywp9hn.ap-southeast-2.rds.amazonaws.com:3306/crisismgmt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "dd02dbe50eb41792067d9d650cd3ba58df0c90c6466ccea7"