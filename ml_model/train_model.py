import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
print("Loading dataset...")
df = pd.read_csv('cattle_disease_dataset.csv')

# Preprocess descriptions
print("Processing descriptions...")
descriptions = df['Description'].values

# Create vectorizers and encode data
print("Vectorizing features...")
description_vectorizer = TfidfVectorizer(min_df=2)
X = description_vectorizer.fit_transform(descriptions)

# Encode disease labels
print("Encoding labels...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['Disease'])

# Split the dataset
print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the models and preprocessors
print("\nSaving models...")
joblib.dump(model, 'cattle_disease_model.pkl')
joblib.dump(description_vectorizer, 'description_vectorizer.pkl')
joblib.dump(label_encoder, 'disease_label_encoder.pkl')

# Print performance metrics
print("\nModel Performance:")
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)
print(f"Training Accuracy: {train_accuracy:.2f}")
print(f"Testing Accuracy: {test_accuracy:.2f}")