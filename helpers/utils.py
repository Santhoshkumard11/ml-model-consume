from ml_model_consume.helpers.constants import model_attributes


def get_model_attributes(model_version) -> dict:
    model_attributes.update({"latest": model_attributes["v2"]})

    return model_attributes[model_version]
