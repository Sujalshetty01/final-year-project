import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Example: Load your data (replace with your actual file)
data = pd.read_csv('data/sample.csv')  # Update path as needed

# Example: Assume 'label' is the target column, rest are features
X = data.drop('label', axis=1)
y = data['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))

# Save model
joblib.dump(clf, 'models/decision_tree_model.pkl')
print('Model saved to models/decision_tree_model.pkl')
