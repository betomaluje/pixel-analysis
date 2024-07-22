import logging
from waitress import serve
from flask import Flask
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from dotenv import find_dotenv, load_dotenv

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

app.config.from_pyfile('settings.py')

bootstrap = Bootstrap(app)

env_file = find_dotenv()
load_dotenv(env_file)

# Initialize MongoDB
MONGO_URI = app.config.get('MONGO_URI')
if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI)
        users_collection = mongo_client['PixelAnalysis']['Users']
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        users_collection = None
else:
    users_collection = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

from routes import *

if __name__ == "__main__":
    serve(app, port='8000', threads=36, channel_timeout=400)