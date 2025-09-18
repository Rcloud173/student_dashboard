# utils/predictions.py

import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans

def get_ml_predictions(model, data):
    df = data.copy()
    df['gender_encoded'] = df['gender'].apply(lambda x: 1 if x.lower() == 'male' else 0)
    features = ['attendance', 'current_test_score', 'current_assignment_score', 'previous_test_score', 'previous_assignment_score', 'fees', 'gender_encoded']
    for col in features:
        if col not in df.columns: st.error(f"Error: Missing column '{col}'"); st.stop()
    X = df[features]
    df['dropout_probability'] = model.predict_proba(X)[:, 1]
    return df

def assign_risk_levels(probabilities):
    if probabilities.empty: return pd.Series()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(probabilities.values.reshape(-1, 1))
    df_temp = pd.DataFrame({'probability': probabilities, 'cluster': clusters})
    cluster_means = df_temp.groupby('cluster')['probability'].mean().sort_values()
    risk_mapping = {cluster_means.index[2]: 'Low', cluster_means.index[1]: 'Medium', cluster_means.index[0]: 'High'}
    return df_temp['cluster'].map(risk_mapping)