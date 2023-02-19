from ml_model_consume.helpers.constants import MODEL_ATTRIBUTES


def get_model_attributes(model_version) -> dict:
    MODEL_ATTRIBUTES.update({"latest": MODEL_ATTRIBUTES["v2"]})

    return MODEL_ATTRIBUTES[model_version]
