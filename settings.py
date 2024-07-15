from os import environ

MONGO_URI = environ.get('MONGO_URI')
SECRET_KEY = environ.get('SECRET_KEY')
WTF_CSRF_SECRET_KEY = environ.get('WTF_CSRF_SECRET_KEY')