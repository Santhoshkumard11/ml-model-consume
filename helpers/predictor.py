import logging
import pandas as pd
import joblib
import json
import os
import urllib.request

# from ml_model_consume.helpers.object_storage_client import LinObjStoClient
from ml_model_consume.helpers.constants import LINODE_OBJECT_STORAGE_MODEL_URL
from ml_model_consume.helpers.utils import get_model_attributes


# using Linode Object Storage
# storage_client = LinObjStoClient()
# storage_client.load_model("ml_model_consume", "96_90_random_forest_nor_10k.sav")

_LATEST_MODEL_VERSION = os.environ.get("LATEST_MODEL_VERSION")

MODEL_V1_PATH = urllib.request.urlopen(LINODE_OBJECT_STORAGE_MODEL_URL)

# load the model and get the model running for prediction
MODEL_V1 = joblib.load(MODEL_V1_PATH)

# label reference
CLASSIFIER_CLASSES_MAPPING_DICT = {0: "safe to consume", 1: "unsafe to consume"}

logger = logging.getLogger()


class Predictor:
    "The class that makes the actual prediction"

    def __init__(self, features_dict: dict, req_body={}) -> None:
        self.features_dict = features_dict
        self.req_body = req_body

        self.model_version, self.flag_probability = req_body.get(
            "model_version", "latest"
        ), req_body.get("get_probability", False)

        self.flag_model_features, self.flag_feature_importance = req_body.get(
            "get_model_features", False
        ), req_body.get("get_feature_importance", False)

        self.model_version = (
            _LATEST_MODEL_VERSION
            if self.model_version == "latest"
            else self.model_version
        )

        self.model_attributes = get_model_attributes(self.model_version)
        self.predict_df = None
        self.model = MODEL_V1

    def preprocess_feature_list(self):
        "Get all the features and convert them to float values then finally to pandas dataframe"

        for key, value in self.features_dict.items():
            self.features_dict.update({key: float(value)})

        self.predict_df = pd.DataFrame(self.features_dict, index=[0])

    def construct_final_output(self, predicted_class: int):
        """Add multiple parameters based on users request body to the response

        Args:
            predicted_class (int): class of the prediction

        Returns:
            str: response to be sent to user
        """

        final_output = {}

        raw_prediction = CLASSIFIER_CLASSES_MAPPING_DICT.get(
            int(predicted_class), "error"
        )

        final_output.update(
            {"prediction": raw_prediction, "predicted_class": predicted_class}
        )

        if self.flag_probability:
            probability = self.model.predict_proba(self.predict_df).tolist()[0]

            final_output.update(
                {"probability": {"0": probability[0], "1": probability[1]}}
            )

        if self.flag_model_features:
            final_output.update(
                {"feature_columns": self.model.feature_names_in_.tolist()}
            )

        if self.flag_feature_importance:
            final_output.update(
                {"feature_importance": self.model.feature_importances_.tolist()}
            )

        return json.dumps(final_output)

    def model_describe(self):
        """Get the model's feature names and importance

        Returns:
            str: response to be sent back
        """

        final_output = {}

        for key, value in zip(
            self.model.feature_names_in_.tolist(),
            self.model.feature_importances_.tolist(),
        ):
            final_output.update({key: value})

        return json.dumps({"feature_importance": final_output})

    def predict(self):
        """Make predictions by loading the image into the session

        Returns:
            str: return the classification
        """

        try:
            logger.info("Attempting to make prediction..")

            predict_output = ""

            self.preprocess_feature_list()

            predict_output = self.model.predict(self.predict_df)

            predicted_class = predict_output.tolist()[0]

            logger.info(f"class - {predicted_class}")

            logger.info("Prediction made successfully!!!")

        except Exception as e:
            logger.exception(f"An error occurred while prediction: {e}")
            raise

        return self.construct_final_output(predicted_class)
