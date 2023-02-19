from ml_model_consume.helpers.constants import MODEL_ATTRIBUTES


def get_model_attributes(model_version: str) -> dict:
    """Get the model details for the given model version

    Args:
        model_version (str): version of the model to use

    Returns:
        dict: model details
    """

    MODEL_ATTRIBUTES.update({"latest": MODEL_ATTRIBUTES["v2"]})

    return MODEL_ATTRIBUTES[model_version]
