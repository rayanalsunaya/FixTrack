import pickle
import pandas as pd
from datetime import date, timedelta
 
with open("usage_model.pkl", "rb") as f:
    model = pickle.load(f)
 
with open("model_columns.pkl", "rb") as f:
    columns = pickle.load(f)
 
# example user for the demo
usage_pattern = 2
preferred_interval = 5000
 
row = pd.DataFrame([[preferred_interval]], columns=["preferred_interval"])
for col in columns:
    if col != "preferred_interval":
        row[col] = 0
 
pattern_col = "usage_pattern_" + str(usage_pattern)
if pattern_col in row.columns:
    row[pattern_col] = 1
 
row = row[columns]
 
predicted_km_per_day = model.predict(row)[0]
 
days_left = preferred_interval / predicted_km_per_day
predicted_date = date.today() + timedelta(days=days_left)
 
print("estimated usage rate:", round(predicted_km_per_day, 1), "km per day")
print("predicted maintenance date:", predicted_date)
