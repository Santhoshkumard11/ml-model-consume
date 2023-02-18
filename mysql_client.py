import mysql.connector
import os
from io import StringIO
import logging
import json
from ml_model_consume.helpers.constants import (
    _ML_LOG_QUERY_ARGS_MAPPING,
    _MISCLASSIFIED_QUERY_ARGS_MAPPING,
    _QUERY_CONSTRUCT_HELPER,
    _INSERT_QUERY_TEMPLATE,
)

logging.info(f'host - {os.environ.get("MYSQL_HOST")}')

MYSQL_CONN = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USERNAME"),
    password=os.environ.get("MYSQL_PASSWORD"),
    port=3306,
    database="ml_model_logs",
    autocommit=True
)


class MySQLClient:
    def __init__(self) -> None:
        self.column_values, self.query_type, self.final_query_to_execute = [], "", ""

    def load_request_response_dicts(self, req_body: dict, response: str):
        self.req_body = req_body
        self.response = json.load(StringIO(response))

    def construct_query(self):
        query_helper = _QUERY_CONSTRUCT_HELPER[self.query_type]

        database_name, table_name, column_names = (
            query_helper.get("database_name"),
            query_helper.get("table_name"),
            query_helper.get("column_names"),
        )

        self.get_column_values()

        self.column_values = str(self.column_values)[1:-1].replace(
            "'default'", "default"
        )

        self.final_query_to_execute = _INSERT_QUERY_TEMPLATE.format(
            database_name=database_name,
            table_name=table_name,
            column_names=column_names,
            column_values=self.column_values,
        )

        logging.info(f"query - {self.final_query_to_execute}")

    def execute_query(self):
        try:
            with MYSQL_CONN.cursor() as cur:
                cur.execute(self.final_query_to_execute)
                logging.info(f"{self.query_type} - executed query!")

        except Exception as e:
            logging.error(f"Error in execute_query - {e}")
            raise

    def get_column_values(self):
        query_args_mapper = (
            _ML_LOG_QUERY_ARGS_MAPPING
            if self.query_type == "ml_model_logs"
            else _MISCLASSIFIED_QUERY_ARGS_MAPPING
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
