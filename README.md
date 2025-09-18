# AI & Expert System Student Risk Dashboard 🎓

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An interactive web application built with Streamlit to identify students at risk of dropping out. This dashboard utilizes a powerful dual-approach, combining a data-driven **AI model** with a knowledge-based **Expert System** to provide both predictive scores and interpretable, actionable insights.



---

## ✨ Features

* **Dual Analysis Views**: Seamlessly switch between an AI-based probabilistic view and a rule-based expert system view.
* **Multi-File Upload**: Upload and automatically merge multiple student data files in both **CSV** and **Excel** formats.
* **Interactive Dashboard**: Visualize high-level metrics, risk distributions, and data relationships with interactive charts from Plotly.
* **Dynamic Filtering**: Drill down into your data by filtering students based on AI risk level, expert system status, or fee payment status.
* **On-the-Fly PDF Reports**: Generate personalized, professional PDF reports for individual students or in bulk for filtered groups.
* **Integrated Emailing**: Directly email generated reports to students. The system uses Streamlit's secrets management for secure handling of email credentials.

---

## 📂 Project Structure

The project is organized into modules for better maintainability and readability.

```
student_dashboard/
│
├──  Mover_Aqui_o_Modelo.joblib      # <-- Place your pre-trained ML model here
│
├── 📄 main_app.py                # Main Streamlit app file (to be run)
├── 📄 config.py                  # Stores constants and thresholds
├── 📄 requirements.txt           # Lists all project dependencies
│
└── 📁 utils/
    ├── 📄 __init__.py            # Makes 'utils' a Python package
    ├── 📄 data_processing.py       # Handles file loading and merging
    ├── 📄 email_sender.py          # Contains the email sending function
    ├── 📄 expert_system.py         # Contains the rule-based logic
    ├── 📄 predictions.py           # Contains the AI/ML prediction logic
    └── 📄 reporting.py             # Contains all PDF generation code
```

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites
* Python 3.8 or higher
* `pip` and `venv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Rcloud173/student_dashboard.git
    cd student_dashboard
    ```

2.  **Create and activate a virtual environment:**
    * **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install the required dependencies:**
    Create a `requirements.txt` file with the content below and then run the `pip install` command.

    **`requirements.txt`:**
    ```
    streamlit
    pandas
    scikit-learn
    joblib
    plotly
    fpdf
    matplotlib
    openpyxl
    ```

    **Installation command:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ⚙️ Configuration

Before running the application, you need to configure two things:

### 1. AI Model
Place your pre-trained machine learning model (e.g., `Mover_Aqui_o_Modelo.joblib`) in the root directory of the project.

### 2. Email Credentials (for Emailing Reports)
The application uses Streamlit's secrets management to handle email credentials securely.

1.  Create a directory named `.streamlit` in the root of your project folder.
2.  Inside the `.streamlit` directory, create a file named `secrets.toml`.
3.  Add your sender email credentials to this file in the following format. For Gmail, you may need to generate an "App Password".

    **`.streamlit/secrets.toml`:**
    ```toml
    # Email credentials for report sending
    sender_email = "your_email@gmail.com"
    sender_password = "your_gmail_app_password"
    ```
    > **Note:** This file is included in `.gitignore` by default in most projects to prevent you from accidentally committing sensitive information.

---

## ▶️ How to Run

Once you have completed the installation and configuration steps, run the application from the root directory using the following command:

```bash
streamlit run main_app.py
```

Your web browser should automatically open with the application running.

---

## 📋 Usage Guide

1.  **Upload Data**: In the sidebar, click "Browse files" to upload one or more student data files (`.csv` or `.xlsx`).
2.  **Upload Model**: Upload your pre-trained `.joblib` model file.
3.  **Predict Risk**: Click the "Predict Risk" button to process the data. An expander will appear in the sidebar allowing you to preview the merged dataset.
4.  **Analyze**: Use the tabs ("Dashboard Overview", "Detailed Student List") to analyze the results. Toggle between the "AI-Based View" and "Rule-Based View".
5.  **Filter**: Use the filters in the sidebar to narrow down the student list.
6.  **Generate Reports**: Navigate to the "Individual Reporting" tab to download or email PDF reports for single students or in bulk for the currently filtered group.
