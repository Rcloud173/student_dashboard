# utils/reporting.py

import io
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Student Risk Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_ai_pdf(student_data, ai_peer_metrics):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"AI-Based Report for: {student_data['Student Name']}", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Gender: {student_data['gender'].title()}", 0, 1)
    pdf.cell(0, 8, f"Fee Status: {'Paid' if student_data['fees'] == 1 else 'Unpaid'}", 0, 1); pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "AI Model Risk Analysis", 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    risk_level = student_data['ai_risk_level']
    color = (255, 75, 75) if risk_level == 'High' else ((255, 195, 0) if risk_level == 'Medium' else (40, 167, 69))
    pdf.set_text_color(*color); pdf.cell(0, 8, f"Predicted AI Risk Level: {risk_level}", 0, 1)
    pdf.set_text_color(0, 0, 0); pdf.cell(0, 8, f"Dropout Probability Score: {student_data['dropout_probability']:.2%}", 0, 1); pdf.ln(5)
    
    pdf.add_page()
    metrics = ['attendance', 'current_test_score']
    student_values = [student_data[m] for m in metrics]
    x_labels = [m.replace('_', ' ').title() for m in metrics]
    fig, ax = plt.subplots(figsize=(7, 4))
    ai_avg_values = [ai_peer_metrics[m] for m in metrics]
    x = np.arange(len(metrics)); width = 0.35
    ax.bar(x - width/2, student_values, width, label=student_data['Student Name'], color='#4A90E2')
    ax.bar(x + width/2, ai_avg_values, width, label=f'Avg. for {risk_level} Risk', color='#D3D3D3')
    ax.set_ylabel('Scores / Percentage'); ax.set_title('Performance vs. AI Peer Group'); ax.set_xticks(x); ax.set_xticklabels(x_labels); ax.legend(); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); buf.seek(0); pdf.image(buf, x=pdf.get_x() + 25, w=160)
    plt.close(fig)
    return bytes(pdf.output())

def generate_rule_based_pdf(student_data, rule_peer_metrics):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"Rule-Based Report for: {student_data['Student Name']}", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Gender: {student_data['gender'].title()}", 0, 1)
    pdf.cell(0, 8, f"Fee Status: {'Paid' if student_data['fees'] == 1 else 'Unpaid'}", 0, 1); pdf.ln(5)

    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "Expert System Analysis", 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    expert_status = student_data['expert_status']
    color = (255, 75, 75) if expert_status == 'Dropout' else ((255, 195, 0) if expert_status == 'Medium' else (40, 167, 69))
    pdf.set_text_color(*color); pdf.cell(0, 8, f"Predicted Status: {expert_status}", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "Reason:", 0, 1)
    pdf.set_font('Arial', '', 12); pdf.multi_cell(0, 8, student_data['expert_reason'])
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "Expert System Suggestion:", 0, 1)
    pdf.set_font('Arial', '', 12); pdf.multi_cell(0, 8, student_data['expert_suggestion'])
    
    pdf.add_page()
    metrics = ['attendance', 'current_test_score']
    student_values = [student_data[m] for m in metrics]
    x_labels = [m.replace('_', ' ').title() for m in metrics]
    fig, ax = plt.subplots(figsize=(7, 4))
    rule_avg_values = [rule_peer_metrics[m] for m in metrics]
    x = np.arange(len(metrics)); width = 0.35
    ax.bar(x - width/2, student_values, width, label=student_data['Student Name'], color='#4A90E2')
    ax.bar(x + width/2, rule_avg_values, width, label=f'Avg. for {expert_status} Status', color='#D3D3D3')
    ax.set_ylabel('Scores / Percentage'); ax.set_title('Performance vs. Rule-Based Peer Group'); ax.set_xticks(x); ax.set_xticklabels(x_labels); ax.legend(); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format='png'); buf.seek(0); pdf.image(buf, x=pdf.get_x() + 25, w=160)
    plt.close(fig)
    return bytes(pdf.output())