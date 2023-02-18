from time import time
import json
from ml_model_consume.helpers.predictor import Predictor
from ml_model_consume.helpers.mysql_client import MySQLClient

global logger


def add_time_to_response(response, end_time):
    from io import StringIO

    string_io = StringIO((response))
    response_json = json.load(string_io)
    response_json.update({"response_time": end_time, "log_source": "linode"})
    return json.dumps(response_json)


def mysql_handler(req_body: dict, response: str, query_type: str):
    mysql_client = MySQLClient()
    if query_type == "ml_model_log":
        mysql_client.add_ml_logs(req_body, response)
    if query_type == "misclassified":
        mysql_client.add_misclassified(req_body, response)


def handle_predict(request, _logger):
    global logger
    logger = _logger

    start_time = time()
    method_type = request.method

    if method_type == "POST":
        req_body = request.get_json()
        features_list = req_body.get("features_dict")
        mode = req_body.get("mode", "predict")
        skip_db_update = req_body.get("skip_db_update", False)

        logger.info("Got a post request")

        if mode == "predict":
            end_time = round(time() - start_time, 4)
            if len(features_list) == 0:
                return (
                    f"""Endpoint hit! \n
                        Pass the features_list in the json body for classification. Response Time - {end_time}""",
                )

            else:
                predictor_obj = Predictor(features_list, req_body)
                logger.info("Making predictions")
                prediction_result = predictor_obj.predict()
                end_time = round(time() - start_time, 4)
                prediction_result = add_time_to_response(prediction_result, end_time)
                if skip_db_update is False:
                    mysql_handler(req_body, prediction_result, "ml_model_log")
                logger.info(f"Done prediction - {end_time}")
                return prediction_result

        elif mode == "model_describe":
            logger.info("Doing model describe")
            predictor_obj = Predictor(features_list, req_body)
            model_result = predictor_obj.model_describe()
            end_time = round(time() - start_time, 4)
            model_result = add_time_to_response(model_result, end_time)
            logger.info(f"Done in - {end_time}")
            return model_result

    elif method_type == "GET":
        return "Send a POST request with the feature values to get the predictions"
