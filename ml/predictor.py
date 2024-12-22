import joblib
import pandas as pd

def load_model(model_path):
    """Load the trained ML model."""
    return joblib.load(model_path)

def prepare_input(task_type, difficulty, task_types_columns):
    """Prepare input data for prediction."""
    input_data = pd.DataFrame(columns=task_types_columns)
    input_data.loc[0, :] = 0  # Initialize all columns with zeros
    if f"task_type_{task_type}" in task_types_columns:
        input_data.loc[0, f"task_type_{task_type}"] = 1
    input_data.loc[0, "difficulty"] = difficulty
    return input_data

def predict_task_duration(model, input_data):
    """Predict task duration."""
    prediction = model.predict(input_data)
    return prediction[0]

import joblib
import pandas as pd

def load_model(model_path):
    """Load the trained ML model."""
    return joblib.load(model_path)

def prepare_input(task_type, difficulty, task_types_columns):
    """Prepare input data for prediction."""
    input_data = pd.DataFrame(columns=task_types_columns)
    input_data.loc[0, :] = 0  # Initialize all columns with zeros
    if f"task_type_{task_type}" in task_types_columns:
        input_data.loc[0, f"task_type_{task_type}"] = 1
    input_data.loc[0, "difficulty"] = difficulty
    return input_data

def predict_task_duration(model, input_data):
    """Predict task duration."""
    prediction = model.predict(input_data)
    return prediction[0]

