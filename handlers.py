import logging
from time import time
import json
from ml_model_consume.helpers.predictor import Predictor
from ml_model_consume.helpers.mysql_client import MySQLClient

logger = logging.getLogger()


def add_time_to_response(response, end_time):
    """Added response time to response json

    Args:
        response (str): response to be sent back
        end_time (float): end time of the prediction

    Returns:
        str: response to be sent back
    """

    from io import StringIO

    string_io = StringIO((response))
    response_json = json.load(string_io)
    response_json.update({"response_time": end_time, "log_source": "linode"})
    return json.dumps(response_json)


def mysql_handler(req_body: dict, response: str, query_type: str):
    """Get the MySQL client and update the database

    Args:
        req_body (dict): request body from the user
        response (str): response to be sent back
        query_type (str): query to be executed in MySQL
    """

    mysql_client = MySQLClient()
    if query_type == "ml_model_log":
        mysql_client.add_ml_logs(req_body, response)
    if query_type == "misclassified":
        mysql_client.add_misclassified(req_body, response)


def handle_predict(request):
    """
        Handle the /predict endpoint

    Args:
        request (object): request object from the Flask app

    Return:
        str: response to be sent back to user
    """

    start_time = time()
    method_type = request.method

    if method_type == "POST":
        # get initial values
        req_body = request.get_json()
        features_list = req_body.get("features_dict")
        mode = req_body.get("mode", "predict")
        skip_db_update = req_body.get("skip_db_update", False)

        logger.info("Got a post request")

        if mode == "predict":
            end_time = round(time() - start_time, 4)

            # if there are no features
            if len(features_list) == 0:
                return (
                    f"""Endpoint hit! <br><br><br>
                        Pass the features_list in the json body for classification. <br><br><br>Response Time - {end_time}<br><br><br>Sandy Inspires""",
                )

            else:
                predictor_obj = Predictor(features_list, req_body)
                logger.info("Making predictions")
                prediction_result = predictor_obj.predict()

                end_time = round(time() - start_time, 4)
                prediction_result = add_time_to_response(prediction_result, end_time)

                # add a log to the MySQL database
                if skip_db_update is False:
                    mysql_handler(req_body, prediction_result, "ml_model_log")
                logger.info(f"Done prediction in {end_time}")

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
        return "Send a POST request with the feature values to get the predictions<br><br><br>Sandy Inspires"
