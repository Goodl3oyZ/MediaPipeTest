import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

X = np.load(os.path.join(DATA_DIR, 'X.npy'))
y = np.load(os.path.join(DATA_DIR, 'y.npy'))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

joblib.dump(clf, os.path.join(DATA_DIR, 'exercise_classifier.joblib'))

print("Model saved to data/exercise_classifier.joblib")
print("Test set classification report:")
print(classification_report(y_test, clf.predict(X_test))) 