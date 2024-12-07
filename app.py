import json
import os

import streamlit as st
from fpdf import FPDF

# File paths
USERS_FILE = 'users.json'
PROJECTS_FILE = 'projects.json'

# Ensure required directories exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as file_users:
        json.dump({}, file_users)

if not os.path.exists(PROJECTS_FILE):
    with open(PROJECTS_FILE, 'w') as file_projects:
        json.dump({}, file_projects)


# Helper functions
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def register_user(username, password):
    users = load_data(USERS_FILE)
    if username in users:
        return False  # User already exists
    users[username] = {'password': password}
    save_data(USERS_FILE, users)
    return True


def authenticate_user(username, password):
    users = load_data(USERS_FILE)
    return users.get(username) and users[username]['password'] == password


def create_project(project_name, client, contract_value, location, start_date, end_date):
    projects = load_data(PROJECTS_FILE)
    if project_name in projects:
        return False  # Project already exists
    projects[project_name] = {
        'client': client,
        'contract_value': contract_value,
        'location': location,
        'start_date': start_date,
        'end_date': end_date,
        'progress': {},
        'documents': [],
        'tasks': [],
        'interim_claims': []
    }
    save_data(PROJECTS_FILE, projects)
    os.makedirs(f"projects/{project_name}", exist_ok=True)
    return True


def view_project(project_name):
    projects = load_data(PROJECTS_FILE)
    return projects.get(project_name)


# PDF Generation for Project Report
def generate_pdf(project_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Project Report: " + project_data["client"], ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt="Project Name: " + project_data["client"], ln=True)
    pdf.cell(200, 10, txt="Contract Value: RM " + str(project_data["contract_value"]), ln=True)
    pdf.cell(200, 10, txt="Location: " + project_data["location"], ln=True)
    pdf.cell(200, 10, txt="Start Date: " + str(project_data["start_date"]), ln=True)
    pdf.cell(200, 10, txt="End Date: " + str(project_data["end_date"]), ln=True)

    # Add progress details
    pdf.cell(200, 10, txt="Progress: ", ln=True)
    for element, progress in project_data["progress"].items():
        pdf.cell(200, 10, txt=f"{element}: {progress}%", ln=True)

    # Save the file
    pdf.output(f"projects/{project_data['client']}/project_report.pdf")


# Streamlit UI
def main():
    st.title("Construction Project Dashboard")

    # User Authentication
    menu = ["Login", "Register", "Add New Project", "View Projects"]
    choice = st.sidebar.selectbox("Select Option", menu)

    # Login Section
    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state['username'] = username
                st.success(f"Welcome {username}")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    # Registration Section
    elif choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match")
            elif register_user(username, password):
                st.success("Registration successful! Please login.")
                st.experimental_rerun()
            else:
                st.error("Username already exists")

    # Add New Project Section
    elif choice == "Add New Project":
        if 'username' not in st.session_state:
            st.warning("Please log in to add a project.")
            st.sidebar.button("Login", on_click=lambda: st.experimental_rerun())
            return

        st.subheader("Add New Project")
        project_name = st.text_input("Project Name")
        client = st.text_input("Client")
        contract_value = st.number_input("Contract Value (RM)", min_value=0.0, format="%.2f")
        location = st.text_input("Location")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if st.button("Add Project"):
            if create_project(project_name, client, contract_value, location, start_date, end_date):
                st.success(f"Project '{project_name}' added successfully!")
                st.experimental_rerun()
            else:
                st.error("Project already exists.")

    # View Projects Section
    elif choice == "View Projects":
        if 'username' not in st.session_state:
            st.warning("Please log in to view projects.")
            st.sidebar.button("Login", on_click=lambda: st.experimental_rerun())
            return

        st.subheader("Existing Projects")
        projects = load_data(PROJECTS_FILE)

        project_names = list(projects.keys())
        selected_project = st.selectbox("Select a Project", project_names)

        if selected_project:
            project_data = view_project(selected_project)
            if project_data:
                st.write(f"**Project Name**: {selected_project}")
                st.write(f"**Client**: {project_data['client']}")
                st.write(f"**Contract Value**: RM {project_data['contract_value']:.2f}")
                st.write(f"**Location**: {project_data['location']}")
                st.write(f"**Start Date**: {project_data['start_date']}")
                st.write(f"**End Date**: {project_data['end_date']}")

                # Project Progress
                st.subheader("Progress Tracking")
                for element, progress in project_data["progress"].items():
                    st.write(f"{element}: {progress}%")

                # Financials
                st.subhe()
