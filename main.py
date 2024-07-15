import logging
from waitress import serve
from routes import create_app

app = create_app()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    serve(app, port='8000')