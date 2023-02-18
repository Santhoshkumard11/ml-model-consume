from flask import Flask, request
from ml_model_consume.handlers import handle_predict

app = Flask(__name__)


# with open("/etc/config.json") as config_file:
#     config = json.load(config_file)


@app.route("/", methods=["GET"])
def index():
    return "Call /predict with required params to make a successful prediction"


@app.route("/test", methods=["GET"])
def test():
    return "Model Prediction Endpoint is workingIt's working"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    return handle_predict(request, app.logger)
