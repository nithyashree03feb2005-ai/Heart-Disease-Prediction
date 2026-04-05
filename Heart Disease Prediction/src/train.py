import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv('../Dataset/heart_disease_data.csv')

# Ensure target column
if 'num' in df.columns:
    df.rename(columns={'num': 'target'}, inplace=True)

# Feature Engineering
df['chol_bp_ratio'] = df['chol'] / df['trestbps']
df['age_group'] = pd.cut(df['age'], bins=[20,40,60,80], labels=[0,1,2]).astype(int)

X = df.drop('target', axis=1)
y = df['target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

pickle.dump(model, open('../models/model.pkl','wb'))
pickle.dump(scaler, open('../models/scaler.pkl','wb'))