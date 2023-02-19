import mysql.connector
import os
from io import StringIO
import logging
import json
from ml_model_consume.helpers.constants import (
    ML_LOG_QUERY_ARGS_MAPPING,
    MISCLASSIFIED_QUERY_ARGS_MAPPING,
    QUERY_CONSTRUCT_HELPER,
    INSERT_QUERY_TEMPLATE,
)

logger = logging.getLogger()

host, user, password = "", "", ""

# check if we are in production or debug mode
if os.path.isfile("/etc/config.json"):
    with open("/etc/config.json") as config_file:
        config = json.load(config_file)
        logger.info("Production Deployment!!")
        host = config.get("MYSQL_HOST")
        user = config.get("MYSQL_USERNAME")
        password = config.get("MYSQL_PASSWORD")
else:
    host = os.environ.get("MYSQL_HOST")
    user = os.environ.get("MYSQL_USERNAME")
    password = os.environ.get("MYSQL_PASSWORD")


logger.info(f'MySQL host - {host}')

MYSQL_CONN = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    port=3306,
    database="ml_model_logs",
    autocommit=True,
)


class MySQLClient:
    "Handle all MySQL transactions"

    def __init__(self) -> None:
        self.column_values, self.query_type, self.final_query_to_execute = [], "", ""

    def load_request_response_dicts(self, req_body: dict, response: str):
        """Initialize the request and response objects

        Args:
            req_body (dict): request object from user
            response (str): response to be sent to user
        """

        self.req_body = req_body
        self.response = json.load(StringIO(response))

    def construct_query(self):
        "Construct the insert query to be executed by adding column names and values"

        query_helper = QUERY_CONSTRUCT_HELPER[self.query_type]

        database_name, table_name, column_names = (
            query_helper.get("database_name"),
            query_helper.get("table_name"),
            query_helper.get("column_names"),
        )

        self.get_column_values()

        final_column_values = str(self.column_values)[1:-1].replace(
            "'default'", "default"
        )

        self.final_query_to_execute = INSERT_QUERY_TEMPLATE.format(
            database_name=database_name,
            table_name=table_name,
            column_names=column_names,
            column_values=final_column_values,
        )

        logger.info(f"query - {self.final_query_to_execute}")

    def execute_query(self):
        "The actual query executing happens here"

        try:
            with MYSQL_CONN.cursor() as cur:
                cur.execute(self.final_query_to_execute)
                logger.info(f"{self.query_type} - executed query!")

        except Exception as e:
            logger.error(f"Error in execute_query - {e}")
            logger.info(f"query - {self.final_query_to_execute}")
            raise

    def get_column_values(self):
        "Add column values from the corresponding objects"

        query_args_mapper = (
            ML_LOG_QUERY_ARGS_MAPPING
            if self.query_type == "ml_model_logs"
            else MISCLASSIFIED_QUERY_ARGS_MAPPING
        )

        for list_value in query_args_mapper.values():
            _from, column_value_name = list_value
            if _from == "req_body":
                value = self.req_body.get(column_value_name, "default")
                if column_value_name == "features_dict":
                    value = f'"{value}"'
                self.column_values.append(value)
            if _from == "response":
                self.column_values.append(
                    self.response.get(column_value_name, "default")
                )

    def add_ml_logs(self, req_body: dict, response: str):
        self.column_values = []
        self.query_type = "ml_model_logs"
        self.load_request_response_dicts(req_body, response)
        self.construct_query()
        self.execute_query()

    def add_misclassified(self, req_body: dict, response: str):
        self.column_values = []
        self.query_type = "misclassified"
        self.load_request_response_dicts(req_body, response)
        self.construct_query()
        self.execute_query()
