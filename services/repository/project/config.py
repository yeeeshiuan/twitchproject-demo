# project/config.py


import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    USERS_SERVICE_URL = os.environ.get('USERS_SERVICE_URL')
    REPOSITORY_URI = os.environ.get('REPOSITORY_URI')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""



class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_TEST_URI')


class StagingConfig(BaseConfig):
    """Staging configuration"""
    TESTING = False


class ProductionConfig(BaseConfig):
    """Production configuration"""
    TESTING = False
