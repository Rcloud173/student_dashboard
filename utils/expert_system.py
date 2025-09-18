# utils/expert_system.py

import pandas as pd
import numpy as np
import streamlit as st
from config import THRESHOLDS # Import thresholds from the config file

def generate_dropout_report(input_df):
    df = input_df.copy()
    required_mappings = {
        'current_test_score': 'Marks', 'previous_test_score': 'Previous Score', 'attendance': 'Attendance (%)',
    }
    for source, target in required_mappings.items():
        if source not in df.columns: st.error(f"Error: Missing column '{source}'"); st.stop()
        df[target] = df[source]
    if 'Average Study Hour' not in df.columns: df['Average Study Hour'] = 2
    df['Fees Status'] = 'Unknown'
    if 'fees' in df.columns: df['Fees Status'] = np.where(df['fees'] == 1, 'Paid', 'Unpaid')
    score_drop = df['Previous Score'] - df['Marks']
    score_improvement = df['Marks'] - df['Previous Score']
    is_disengaged = (df['Marks'] < THRESHOLDS['MARKS_FAILING']) & (df['Attendance (%)'] < THRESHOLDS['ATTENDANCE_CRITICAL'])
    is_high_achiever_crisis = (df['Previous Score'] > THRESHOLDS['PREVIOUS_SCORE_HIGH']) & (score_drop > THRESHOLDS['SCORE_DROP_SIGNIFICANT']) & (df['Attendance (%)'] < THRESHOLDS['ATTENDANCE_POOR'])
    is_silent_struggler = (df['Marks'] < THRESHOLDS['MARKS_FAILING']) & (df['Attendance (%)'] > THRESHOLDS['ATTENDANCE_POOR']) & (df['Average Study Hour'] >= THRESHOLDS['STUDY_HOURS_HIGH'])
    warning_count = ((df['Marks'] <= THRESHOLDS['MARKS_BORDERLINE']).astype(int) + (df['Attendance (%)'] <= THRESHOLDS['ATTENDANCE_POOR']).astype(int) + (df['Average Study Hour'] <= THRESHOLDS['STUDY_HOURS_LOW']).astype(int) + (df['Fees Status'] == 'Unpaid').astype(int))
    is_coasting = (warning_count >= 2)
    is_declining = (score_drop > THRESHOLDS['SCORE_DROP_MODERATE']) & (df['Attendance (%)'] < THRESHOLDS['ATTENDANCE_POOR'])
    is_fee_risk = (df['Fees Status'] == 'Unpaid')
    has_positive_momentum = (score_improvement > 10) & (df['Attendance (%)'] > THRESHOLDS['ATTENDANCE_POOR'])
    is_stable_performer = (df['Marks'] > THRESHOLDS['MARKS_GOOD']) & (df['Attendance (%)'] > THRESHOLDS['ATTENDANCE_POOR'])
    conditions = [is_disengaged, is_high_achiever_crisis, is_silent_struggler, is_coasting, is_declining, is_fee_risk, has_positive_momentum, is_stable_performer]
    outcomes_status = ['Dropout', 'Dropout', 'Dropout', 'Medium', 'Medium', 'Medium', 'Not Dropout', 'Not Dropout']
    outcomes_reason = ['Disengaged Student', 'High-Achiever in Crisis', 'Silent Struggler', 'Coasting (Multiple warnings)', 'Declining Performer', 'Administrative Risk (Fees)', 'Positive Momentum', 'Stable Performer']
    outcomes_suggestion = ['Suggestion: Immediate, direct intervention required.', 'Suggestion: Urgent, sensitive mentoring needed.', 'Suggestion: Provide academic support.', 'Suggestion: Schedule a check-in.', 'Suggestion: Proactive counseling to reverse the trend.', 'Suggestion: Alert student and guardian about fee status.', 'Suggestion: Acknowledge and encourage progress.', 'Suggestion: Continue standard monitoring.']
    df['expert_status'] = np.select(conditions, outcomes_status, default='Not Dropout')
    df['expert_reason'] = np.select(conditions, outcomes_reason, default='Low Risk Profile')
    df['expert_suggestion'] = np.select(conditions, outcomes_suggestion, default='Suggestion: Continue standard monitoring.')
    return df[['expert_status', 'expert_reason', 'expert_suggestion']]