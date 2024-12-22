# functii pentru antrenarea modelului

import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

def load_data(database_path):
    """Extracts task data from the database."""
    query = """
        SELECT 
            t.title AS task_type,
            t.difficulty,
            tc.completion_time
        FROM 
            tasks t
        INNER JOIN 
            task_completions tc 
        ON 
            t.id = tc.task_id
    """
    connection = sqlite3.connect(database_path)
    df = pd.read_sql_query(query, connection)
    connection.close()
    return df

def preprocess_data(df):
    """Preprocess data: handle NaNs and encode categorical variables."""
    df = df.dropna()
    df = pd.get_dummies(df, columns=["task_type"], drop_first=True)
    X = df.drop("completion_time", axis=1)
    y = df["completion_time"]
    return X, y

def train_model(X, y):
    """Train a Random Forest Regressor."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    return model

def save_model(model, output_path):
    """Save the trained model to a file."""
    joblib.dump(model, output_path)

if __name__ == "__main__":
    database_path = "../tasks.db"
    model_output_path = "./models/task_duration.pkl"
    data = load_data(database_path)
    X, y = preprocess_data(data)
    model = train_model(X, y)
    save_model(model, model_output_path)
