import os
from dotenv import load_dotenv

load_dotenv()


class Development(object):
    """
    Development environment configuration
    """

    DEBUG = True
    TESTING = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("MYSQL_DB")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(object):
    """
    Production environment configurations
    """

    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("PROD_DB_URL")


app_config = {
    "development": Development,
    "production": Production,
}
