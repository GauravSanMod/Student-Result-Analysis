
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score,confusion_matrix
#from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle

df = pd.read_csv('Dataset21.csv')
X = df.drop("Result", axis=1)
y = df["Result"]
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=60)
#scaler = StandardScaler()
#X_train = scaler.fit_transform(X_train)
#X_test = scaler.transform(X_test)
svm_classifier = SVC(kernel="rbf")
svm_classifier.fit(X_train,y_train)
prediction = svm_classifier.predict(X_test)
accuracy = accuracy_score(y_test, prediction)
confusion_matrix(y_test, prediction)

#file handling
load_data = {'model': svm_classifier, 'x_test': X_test, 'y_test': y_test}
with open("svm_model.pkl", "wb") as file:
    pickle.dump(load_data, file)