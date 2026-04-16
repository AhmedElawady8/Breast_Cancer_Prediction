import pickle
import json
import numpy as np


with open("logistic_model.pkl","rb") as f:
    model = pickle.load(f)

with open("scaler.pkl","rb") as f:
    scaler = pickle.load(f)

with open("feature_names.json","r") as f:
    features = json.load(f)


print("Features count:", len(features))
print(features)


test_input = np.random.rand(len(features))  
scaled = scaler.transform(test_input.reshape(1, -1))
pred = model.predict(scaled)
proba = model.predict_proba(scaled)

print("Prediction:", pred)
print("Probability:", proba)
