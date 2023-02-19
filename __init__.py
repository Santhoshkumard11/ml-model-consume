from flask import Flask, request
from ml_model_consume.handlers import handle_predict
import logging
from logging.config import dictConfig

# configuring a custom logger
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
                "level": "INFO",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

logger = logging.getLogger()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    logger.info("Index endpoint hit!")
    return "Index endpoint hit!!<br><br>Make a POST request to /predict with required arguments in JSON body to make a successful prediction <br><br><br>Sandy Inspires"


@app.route("/test", methods=["GET"])
def test():
    logger.info("test endpoint hit!")
    return "Test endpoint hit!!<br><br>Model Prediction Endpoint is working<br><br> Make a POST request to /predict with JSON body <br><br><br> Sandy Inspires"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    logger.info("Predict endpoint hit!")
    return handle_predict(request)
