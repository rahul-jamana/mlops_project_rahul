import joblib
import pandas as pd

model = joblib.load("models/model_v1.pkl")

def predict(hours):
    df = pd.DataFrame({
        "hours": [hours],
        "hours_squared": [hours**2]
    })
    return model.predict(df)[0]