import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold,cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import roc_curve , auc
from save_figures_auto import save_current_plot
import pickle

"""##Load and Read the data"""

data=pd.read_csv(r"data/breast_cancer (2).csv")
data

data.info()

"""#Preprocessing

"""

data.drop(["id","Unnamed: 32"],axis=1,inplace=True)
data.head()

data.describe()

data.isna().sum()

#Duplicated of data
print(data.duplicated().sum())

#Convert M--->1 and B--->0
data["diagnosis"] = [1 if value=="M" else 0 for value in data["diagnosis"]]
data["diagnosis"].value_counts()

#Histogram for all columns in data
data.hist(bins=50, figsize=(20, 15))
plt.tight_layout()
save_current_plot()  
plt.show()

sns.countplot(x=data["diagnosis"],data=data,hue="diagnosis",palette=["#FF5733", "#33C1FF"])
plt.title("Distribution of diagnosis (Malignan=1,Benign=0)")
save_current_plot()  
plt.show()

# Heatmap showing correlations between features
plt.figure(figsize=(40,30))
sns.heatmap(data.corr(),annot=True)
save_current_plot()  
plt.show()

# Calculate correlations of all features with Target'diagnosis' and sort them
correlations = data.corr()['diagnosis'].sort_values(ascending=False)
correlations

#Drop for columns with law corr with Target
data.drop(["symmetry_se","texture_se","fractal_dimension_mean","smoothness_se"],axis=1,inplace=True)

#Determine the Features columns and Target column
X=data.drop(["diagnosis"],axis=1)
y=data["diagnosis"]

# Apply StandardScaler to standardize features (mean=0, std=1)
scaler=StandardScaler()
X=scaler.fit_transform(X)

X

#Split for data to X_train , X_test, y_train, y_test
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=42)
print(X_train.shape)
print(X_test.shape)

"""##LogisticRegression"""

# Create Model
leg=LogisticRegression()

"""#Cross Validation"""

#Cross Validation
# Perform 5fold cross validation to evaluate the model's performance on different subsets of the data
kf=KFold(n_splits=5,shuffle=True,random_state=42)
cross_score=cross_val_score(leg,X,y,cv=kf)
print(cross_score)

#Train MOdel
leg.fit(X_train,y_train)
#y prediction
y_pred=leg.predict(X_test)

print(y_pred)

# Check predicted vs actual label counts and overall accuracy
print(pd.Series(y_pred).value_counts())
print("-"*50)
print(pd.Series(y_test).value_counts())
print("-"*50)

# Show test accuracy by comparing predictions with actual labels
print("Accuracy: ",accuracy_score(y_test,y_pred))

# Show how well the model predicted each class
plt.figure(figsize=(6,5))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Benign (0)', 'Malignant (1)'],
            yticklabels=['Benign (0)', 'Malignant (1)'])
plt.xlabel(' Predicted Label')
plt.ylabel('True Label')
plt.title('Logistic Confusion Matrix')
save_current_plot()  
plt.show()

# Show detailed metrics (precision, recall, f1-score) for each class
print(classification_report(y_test,y_pred))

# Calculate and print the training and testing accuracy of the model
train_acc = leg.score(X_train, y_train)
test_acc = leg.score(X_test, y_test)

print("train_accuracy:",train_acc,"\ntest_accuracy:" ,test_acc)
# Dictionary to store models and their names
models = {
    "Logistic Regression": leg,


}

plt.figure(figsize=(10,8))

for name, mdl in models.items():
    # Compute predicted probabilities for the positive class
    y_prob = mdl.predict_proba(X_test)[:, 1]

    # Compute ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)

    # Compute AUC
    roc_auc = auc(fpr, tpr)

    # Plot ROC curve
    plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.2f})')

# Plot random classifier line
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')

plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves for All Models')
plt.legend(loc="lower right")
plt.grid(True)
save_current_plot()  
plt.show() 

import os
import pickle
import json

print("Save using pickle to current directory")

# Save feature names
features = data.drop(["diagnosis"], axis=1).columns.tolist()
with open("feature_names.json", "w") as f:
    json.dump(features, f)

# Save the trained model
with open("logistic_model.pkl", "wb") as f:
    pickle.dump(leg, f)

# Save the scaler
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("Saved. file sizes:")
print("logistic_model.pkl ->", os.path.getsize("logistic_model.pkl"))
print("scaler.pkl ->", os.path.getsize("scaler.pkl"))
