# utils/data_processing.py

import streamlit as st
import pandas as pd
import joblib

@st.cache_data
def load_and_merge_files(uploaded_files):
    """
    Loads multiple CSV and Excel files, merges them, and returns a single DataFrame.
    """
    if not uploaded_files:
        return None
    
    dataframes = []
    for file in uploaded_files:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
                dataframes.append(df)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
                dataframes.append(df)
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            return None
            
    if not dataframes:
        st.warning("No valid files were processed.")
        return None
        
    try:
        merged_df = pd.concat(dataframes, ignore_index=True)
        return merged_df
    except Exception as e:
        st.error(f"Failed to merge files. Ensure columns match. Error: {e}")
        return None

@st.cache_resource
def load_model(_uploaded_file):
    """
    Loads a joblib model from an uploaded file.
    """
    try:
        return joblib.load(_uploaded_file)
    except Exception as e:
        st.error(f"Error loading model file: {e}")
        return None