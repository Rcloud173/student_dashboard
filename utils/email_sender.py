# utils/email_sender.py

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_with_attachment(recipient_email, subject, body, pdf_data, student_name, report_type):
    """Securely sends an email with the PDF report attached."""
    try:
        if 'sender_email' not in st.secrets or 'sender_password' not in st.secrets:
            st.error("Email credentials are not configured in secrets.toml. Cannot send email.")
            return False

        sender_email = st.secrets["sender_email"]
        sender_password = st.secrets["sender_password"]

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        pdf_attachment = MIMEApplication(pdf_data, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f"{report_type}_Report_{student_name.replace(' ', '_')}.pdf")
        msg.attach(pdf_attachment)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Failed to send email to {recipient_email}: {e}")
        return False