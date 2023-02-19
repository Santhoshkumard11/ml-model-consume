from flask import Flask, request
from ml_model_consume.handlers import handle_predict
import logging
from logging.config import dictConfig

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
    logger.info("index called")
    return "Call /predict with required params to make a successful prediction"


@app.route("/test", methods=["GET"])
def test():
    logger.info("test endpoint hit!")
    return "Model Prediction Endpoint is workingIt's working"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    logger.info("Predict endpoint hit!")
    return handle_predict(request)
