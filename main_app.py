# main_app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Import functions from your new utility modules
from utils.data_processing import load_and_merge_files, load_model
from utils.predictions import get_ml_predictions, assign_risk_levels
from utils.expert_system import generate_dropout_report
from utils.reporting import generate_ai_pdf, generate_rule_based_pdf
from utils.email_sender import send_email_with_attachment

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI & Expert System Student Dashboard",
    page_icon="🎓",
    layout="wide",
)

# --- MAIN APP INTERFACE ---
st.title("🎓 Student Prediction Dashboard")

# Initialize session state variables
if 'predictions_df' not in st.session_state:
    st.session_state.predictions_df = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'ai'
if 'merged_data' not in st.session_state:
    st.session_state.merged_data = None

# --- SIDEBAR FOR FILE UPLOADS AND CONTROLS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # UPDATED: File uploader to accept multiple files
    uploaded_files = st.file_uploader(
        "1. Upload Student Data (CSV or Excel)",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )
    
    uploaded_model = st.file_uploader("2. Upload AI Model (.joblib)", type=["joblib", "pkl"])

    if st.button("Predict Risk", type="primary", use_container_width=True, disabled=not (uploaded_files and uploaded_model)):
        # NEW: Load and merge data first
        data = load_and_merge_files(uploaded_files)
        st.session_state.merged_data = data # Store merged data for display
        
        model = load_model(uploaded_model)
        
        if model and data is not None:
            with st.spinner('Running predictions...'):
                df_ml = get_ml_predictions(model, data)
                df_ml['ai_risk_level'] = assign_risk_levels(df_ml['dropout_probability'])
                df_expert = generate_dropout_report(data)
                st.session_state.predictions_df = pd.concat([df_ml, df_expert], axis=1)
    st.markdown("---")
    
    # NEW: Expander to show the merged data
    if st.session_state.merged_data is not None:
        with st.expander("View Merged Data"):
            st.dataframe(st.session_state.merged_data)

# --- MAIN PANEL DISPLAY ---
if st.session_state.predictions_df is not None:
    df = st.session_state.predictions_df
    # RENAME 'Student Name' column for easier attribute access
    if 'Student Name' in df.columns:
        df = df.rename(columns={'Student Name': 'Student_Name'})
        st.session_state.predictions_df = df # Update session state

    is_ai_view = st.session_state.view_mode == 'ai'
    c1, c2 = st.columns(2)
    if c1.button("🤖 AI-Based View", use_container_width=True, type="primary" if is_ai_view else "secondary"):
        st.session_state.view_mode = 'ai'
    if c2.button("⚖️ Rule-Based View", use_container_width=True, type="primary" if not is_ai_view else "secondary"):
        st.session_state.view_mode = 'rule'

    # Sidebar filters (appear after prediction)
    st.sidebar.header("📊 Filter Students")
    if is_ai_view:
        options = sorted(df['ai_risk_level'].unique())
        selection = st.sidebar.multiselect("Filter by AI Risk Level", options=options, default=options)
        filtered_df = df[df['ai_risk_level'].isin(selection)]
    else:
        options = sorted(df['expert_status'].unique())
        selection = st.sidebar.multiselect("Filter by Expert Status", options=options, default=options)
        filtered_df = df[df['expert_status'].isin(selection)]
    
    fee_filter = st.sidebar.selectbox("Filter by Fee Status", options=['All', 'Paid', 'Unpaid'])
    if fee_filter != 'All':
        fee_val = 1 if fee_filter == 'Paid' else 0
        filtered_df = filtered_df[filtered_df['fees'] == fee_val]
    
    # --- TABS FOR DISPLAYING RESULTS ---
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Overview", "📋 Detailed Student List", "📄 Individual Reporting"])
    
    # --- TAB 1: DASHBOARD OVERVIEW ---
    with tab1:
        if is_ai_view:
            st.subheader("AI Model: High-Level Metrics")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(label="**Filtered Students**", value=len(filtered_df))
            kpi2.metric(label="**High-Risk Students**", value=filtered_df[filtered_df['ai_risk_level'] == 'High'].shape[0])
            avg_prob = filtered_df['dropout_probability'].mean() if not filtered_df.empty else 0
            kpi3.metric(label="**Avg. Dropout Probability**", value=f"{avg_prob:.2%}")
            st.markdown("---")
            st.subheader("AI Model: Visualizations")
            col1, col2 = st.columns(2)
            color_map = {'High': '#FF4B4B', 'Medium': '#FFC300', 'Low': '#28A745'}
            with col1:
                st.markdown("##### Risk Level Distribution")
                if not filtered_df.empty:
                    risk_counts = filtered_df['ai_risk_level'].value_counts()
                    fig_pie = px.pie(values=risk_counts.values, names=risk_counts.index, hole=0.4, 
                                     color=risk_counts.index, color_discrete_map=color_map)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No data to display for the current filter.")
            with col2:
                st.markdown("##### Attendance vs. Dropout Probability")
                if not filtered_df.empty:
                    fig_scatter = px.scatter(filtered_df, x='attendance', y='dropout_probability', 
                                             color='ai_risk_level', color_discrete_map=color_map,
                                             labels={'attendance': 'Attendance (%)', 'dropout_probability': 'Dropout Probability'})
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("No data to display for the current filter.")
        else: # Rule-Based View
            st.subheader("Expert System: High-Level Metrics")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(label="**Filtered Students**", value=len(filtered_df))
            kpi2.metric(label="**'Dropout' Status**", value=filtered_df[filtered_df['expert_status'] == 'Dropout'].shape[0])
            kpi3.metric(label="**'Medium' Status**", value=filtered_df[filtered_df['expert_status'] == 'Medium'].shape[0])
            st.markdown("---")
            st.subheader("Expert System: Visualizations")
            col1, col2 = st.columns(2)
            expert_color_map = {'Dropout': '#FF4B4B', 'Medium': '#FFC300', 'Not Dropout': '#28A745'}
            with col1:
                st.markdown("##### Status Distribution")
                if not filtered_df.empty:
                    expert_counts = filtered_df['expert_status'].value_counts()
                    fig_bar = px.bar(expert_counts, x=expert_counts.index, y=expert_counts.values,
                                     color=expert_counts.index, color_discrete_map=expert_color_map,
                                     labels={'x':'Status', 'y':'Number of Students'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("No data to display for the current filter.")
            with col2:
                st.markdown("##### Breakdown of Reasons for 'Dropout' & 'Medium'")
                if not filtered_df.empty:
                    reason_df = filtered_df[filtered_df['expert_status'].isin(['Dropout', 'Medium'])]
                    if not reason_df.empty:
                        reason_counts = reason_df['expert_reason'].value_counts()
                        fig_hbar = px.bar(reason_counts, y=reason_counts.index, x=reason_counts.values, 
                                          orientation='h', labels={'y':'Reason', 'x':'Number of Students'},
                                          title="Reasons for At-Risk Status")
                        fig_hbar.update_layout(yaxis={'categoryorder':'total ascending'})
                        st.plotly_chart(fig_hbar, use_container_width=True)
                    else:
                        st.info("No 'Dropout' or 'Medium' status students in the current filter.")
                else:
                    st.info("No data to display for the current filter.")

    # --- TAB 2: DETAILED STUDENT LIST ---
    with tab2:
        with st.expander("View and Filter Student List 👁️", expanded=True):
            if not filtered_df.empty:
                all_columns = filtered_df.columns.tolist()
                default_columns = [
                    'Student_Name', 'ai_risk_level', 'dropout_probability', 'expert_status', 
                    'current_test_score', 'attendance', 'fees'
                ]
                default_selection = [col for col in default_columns if col in all_columns]

                st.markdown("##### Select Columns to Display")
                selected_columns = st.multiselect(
                    "Filter columns:",
                    options=all_columns,
                    default=default_selection,
                    label_visibility="collapsed"
                )
                st.markdown("---")

                if not selected_columns:
                    st.warning("Please select at least one column to display.")
                else:
                    display_df = filtered_df[selected_columns].copy()
                    if 'dropout_probability' in display_df.columns:
                        display_df['dropout_probability'] = display_df['dropout_probability'].map('{:.2%}'.format)
                    if 'fees' in display_df.columns:
                        display_df['fees'] = display_df['fees'].apply(lambda x: 'Paid' if x == 1 else 'Unpaid')
                        
                    rename_mapping = {
                        'Student_Name': 'Student Name', 'ai_risk_level': 'AI Risk', 'dropout_probability': 'AI Probability',
                        'expert_status': 'Expert Status', 'expert_reason': 'Expert Reason',
                        'current_test_score': 'Test Score', 'attendance': 'Attendance (%)', 'fees': 'Fee Status',
                        'gender': 'Gender', 'previous_test_score': 'Previous Score'
                    }
                    columns_to_rename = {k: v for k, v in rename_mapping.items() if k in display_df.columns}
                    display_df = display_df.rename(columns=columns_to_rename)
                    st.table(display_df)
            else:
                st.info("No students match the current filter criteria.")

    # --- TAB 3: INDIVIDUAL REPORTING ---
    with tab3:
        st.subheader("Send Report to a Single Student")
        
        if not filtered_df.empty:
            student_list = filtered_df['Student_Name'].tolist()
            selected_student_name = st.selectbox("Select a student to generate a report:", student_list, key="single_student_select")
            report_type_single = st.radio("Select Report Type to Generate", ('AI-Based Report', 'Rule-Based Report'), key="single_report_type", horizontal=True)

            if selected_student_name:
                student_data_series = filtered_df[filtered_df['Student_Name'] == selected_student_name].iloc[0]
                
                pdf_student_data = student_data_series.copy()
                # Ensure the original 'Student Name' with space is used for PDF title
                pdf_student_data['Student Name'] = selected_student_name
                
                pdf_data = b""; report_prefix = ""

                if report_type_single == 'AI-Based Report':
                    ai_risk_group = student_data_series['ai_risk_level']
                    ai_peer_metrics = {'attendance': df[df['ai_risk_level'] == ai_risk_group]['attendance'].mean(), 'current_test_score': df[df['ai_risk_level'] == ai_risk_group]['current_test_score'].mean()}
                    pdf_data = generate_ai_pdf(pdf_student_data, ai_peer_metrics)
                    report_prefix = "AI_Based"
                else: # Rule-Based Report
                    rule_status_group = student_data_series['expert_status']
                    rule_peer_metrics = {'attendance': df[df['expert_status'] == rule_status_group]['attendance'].mean(), 'current_test_score': df[df['expert_status'] == rule_status_group]['current_test_score'].mean()}
                    pdf_data = generate_rule_based_pdf(pdf_student_data, rule_peer_metrics)
                    report_prefix = "Rule_Based"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(label=f"📄 Download {report_prefix.replace('_', ' ')}", data=pdf_data,
                                       file_name=f"{report_prefix}_Report_{selected_student_name.replace(' ', '_')}.pdf",
                                       mime="application/pdf", use_container_width=True)
                with col2:
                    email_column_name = 'student_email'
                    email_found = email_column_name in student_data_series.index and pd.notna(student_data_series[email_column_name])
                    
                    if st.button(f"📧 Email Report to {selected_student_name}", use_container_width=True, disabled=not email_found):
                        if 'sender_email' in st.secrets and 'sender_password' in st.secrets:
                            recipient_email = student_data_series[email_column_name]
                            subject = f"{report_type_single} for {selected_student_name}"
                            body = f"Hello,\n\nPlease find the attached {report_type_single.lower()} for {selected_student_name}.\n\nBest regards,"
                            if send_email_with_attachment(recipient_email, subject, body, pdf_data, selected_student_name, report_prefix):
                                st.success(f"Report successfully sent to {recipient_email}!")
                        else:
                            st.warning("Auto-sending is not configured in your secrets.toml file.")
                    if not email_found:
                        st.caption(f"No email found for this student in column '{email_column_name}'.")
        else:
            st.warning("No students available based on current filters.")

        st.markdown("---")

        st.subheader("Send Reports to Multiple Students (Bulk)")
        
        if not filtered_df.empty:
            st.info(f"Your current filters match **{len(filtered_df)}** students.")
            secrets_configured = 'sender_email' in st.secrets and 'sender_password' in st.secrets
            
            report_type_bulk = st.radio("Select Report Type for Bulk Sending", ('AI-Based Report', 'Rule-Based Report'), key="bulk_report_type", horizontal=True)

            if st.button(f"📧 Send {report_type_bulk}s to {len(filtered_df)} Filtered Students", type="primary", use_container_width=True, disabled=not secrets_configured):
                success_list = []; fail_list = []
                email_column_name = 'student_email'
                report_prefix = "AI_Based" if report_type_bulk == 'AI-Based Report' else "Rule_Based"

                progress_bar = st.progress(0, text="Initializing bulk send...")
                
                for i, student_tuple in enumerate(filtered_df.itertuples(index=False)):
                    student_data = pd.Series(student_tuple, index=filtered_df.columns)
                    student_name = student_data['Student_Name']
                    
                    progress_text = f"Processing report for: {student_name}"
                    progress_bar.progress((i + 1) / len(filtered_df), text=progress_text)
                    
                    if email_column_name not in student_data.index or pd.isna(student_data[email_column_name]):
                        st.toast(f"Skipping {student_name}: Email ID does not exist.", icon="⚠️")
                        fail_list.append(f"{student_name} (Missing Email)")
                        continue
                    
                    pdf_student_data = student_data.copy()
                    pdf_student_data['Student Name'] = student_data['Student_Name']
                    pdf_data_bulk = b""

                    if report_type_bulk == 'AI-Based Report':
                        ai_risk_group = student_data['ai_risk_level']
                        ai_peer_metrics = {'attendance': df[df['ai_risk_level'] == ai_risk_group]['attendance'].mean(), 'current_test_score': df[df['ai_risk_level'] == ai_risk_group]['current_test_score'].mean()}
                        pdf_data_bulk = generate_ai_pdf(pdf_student_data, ai_peer_metrics)
                    else: # Rule-Based Report
                        rule_status_group = student_data['expert_status']
                        rule_peer_metrics = {'attendance': df[df['expert_status'] == rule_status_group]['attendance'].mean(), 'current_test_score': df[df['expert_status'] == rule_status_group]['current_test_score'].mean()}
                        pdf_data_bulk = generate_rule_based_pdf(pdf_student_data, rule_peer_metrics)
                        
                    recipient_email = student_data[email_column_name]
                    subject = f"Your Student Performance Report ({report_prefix.replace('_', ' ')})"
                    body = f"Hello {student_name},\n\nPlease find your attached {report_type_bulk.lower()}.\n\nBest regards,"
                    
                    if send_email_with_attachment(recipient_email, subject, body, pdf_data_bulk, student_name, report_prefix):
                        success_list.append(student_name)
                    else:
                        fail_list.append(f"{student_name} (Send Error)")

                progress_bar.empty()
                st.success(f"**Bulk Send Complete!** Successfully sent reports to {len(success_list)} students.")
                if fail_list:
                    st.warning(f"Could not send reports to {len(fail_list)} students:")
                    st.json(fail_list)
            
            if not secrets_configured:
                st.warning("Bulk sending is disabled. Please configure your email credentials in secrets.toml.")
        else:
            st.warning("No students to process. Adjust your filters to select a group of students.")
else:
    st.info("**Welcome!** Upload your data and model in the sidebar to begin.")