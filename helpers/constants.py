model_attributes = {
    "v1": {
        "model_name": "v1",
        "features_list": [
            "pH",
            "Iron",
            "Nitrate",
            "Chloride",
            "Lead",
            "Zinc",
            "Turbidity",
            "Fluoride",
            "Copper",
            "Odor",
            "Sulfate",
            "Chlorine",
            "Manganese",
            "Total Dissolved Solids",
        ],
    },
    "v2": {
        "model_name": "v2",
        "features_list": [
            "pH",
            "Iron",
            "Nitrate",
            "Chloride",
            "Lead",
            "Zinc",
            "Turbidity",
            "Fluoride",
            "Copper",
            "Odor",
            "Sulfate",
            "Conductivity",
            "Chlorine",
            "Manganese",
            "Total Dissolved Solids",
            "Water Temperature",
            "Air Temperature",
            "Day",
            "Time of Day",
            "Target",
            "clr_Colorless",
            "clr_Faint Yellow",
            "clr_Light Yellow",
            "clr_Near Colorless",
            "clr_Yellow",
            "src_Aquifer",
            "src_Ground",
            "src_Lake",
            "src_Reservoir",
            "src_River",
            "src_Spring",
            "src_Stream",
        ],
    },
}


_ML_LOG_QUERY_ARGS_MAPPING = {
    "model_version": ["req_body", "model_version"],
    "features_dict": ["req_body", "features_dict"],
    "predicted_class": ["response", "predicted_class"],
    "response_time": ["response", "response_time"],
    "_mode": ["req_body", "mode"],
    "get_probability": ["req_body", "get_probability"],
    "get_feature_importance": ["req_body", "get_feature_importance"],
    "get_model_features": ["req_body", "get_model_features"],
    "status_code": ["response", "status_code"],
    "log_source": ["response", "log_source"],
}

_MISCLASSIFIED_QUERY_ARGS_MAPPING = {
    "model_version": ["req_body", "model_version"],
    "features_dict": ["req_body", "features_dict"],
    "response_time": ["response", "response_time"],
    "_mode": ["req_body", "mode"],
    "get_probability": ["req_body", "get_probability"],
    "get_feature_importance": ["req_body", "get_feature_importance"],
    "get_model_features": ["req_body", "get_model_features"],
    "status_code": ["response", "status_code"],
}

_QUERY_CONSTRUCT_HELPER = {
    "ml_model_logs": {"table_name": "fresh_water_classifier", "database_name": "ml_model_logs", "column_names": "model_version,features_dict,predicted_class,response_time,_mode,get_probability,get_feature_importance,get_model_features,status_code,log_source"},
    "misclassified": {"table_name": "misclassified", "database_name": "retrain_model", "column_names": "original_class,predicted_class,features_dict,model_version,response_time"},
}


_INSERT_QUERY_TEMPLATE = """INSERT INTO {database_name}.{table_name} ({column_names})  values ({column_values})"""
