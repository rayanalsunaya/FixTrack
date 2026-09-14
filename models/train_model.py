import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import pickle
 
data = pd.read_csv("training_data.csv")
 
# turn usage_pattern into columns the model can use
data = pd.get_dummies(data, columns=["usage_pattern"])
 
x = data.drop("km_per_day", axis=1)
y = data["km_per_day"]
 
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1)
 
model = LinearRegression()
model.fit(x_train, y_train)
 
predictions = model.predict(x_test)
error = mean_absolute_error(y_test, predictions)
 
print("average error:", round(error, 2), "km per day")
 
with open("usage_model.pkl", "wb") as f:
    pickle.dump(model, f)
 
with open("model_columns.pkl", "wb") as f:
    pickle.dump(x.columns.tolist(), f)
 
print("model saved")
