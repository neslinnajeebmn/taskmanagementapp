import streamlit as st
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

# Initialize SQLite database connection
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()

def create_tables():
    """Create the necessary tables if they do not exist."""
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            status TEXT,
            due_date DATE,
            priority TEXT,
            file_data BLOB,
            file_name TEXT,
            assigned_to TEXT,
            assigned_by TEXT,
            FOREIGN KEY (assigned_to) REFERENCES users(name),
            FOREIGN KEY (assigned_by) REFERENCES users(name)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    conn.commit()

create_tables()

def update_table_schema():
    """Update the table schema if needed."""
    try:
        # Check if columns exist before adding
        c.execute('PRAGMA table_info(tasks)')
        columns = [column[1] for column in c.fetchall()]
        if 'file_data' not in columns:
            c.execute('ALTER TABLE tasks ADD COLUMN file_data BLOB')
        conn.commit()
    except sqlite3.OperationalError:
        # Handle any issues with schema updates
        pass

update_table_schema()

def populate_initial_data():
    """Populate initial data if tables are empty."""
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:  # No users found
        # Add default user
        default_user = ('example@example.com', 'Example User')
        c.execute('INSERT INTO users (email, name) VALUES (?, ?)', default_user)
        conn.commit()

populate_initial_data()

def add_task_to_db(task_name, status, due_date, priority, file_data, file_name, assigned_to, assigned_by):
    """Add a new task to the database."""
    c.execute('''
        INSERT INTO tasks (task_name, status, due_date, priority, file_data, file_name, assigned_to, assigned_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (task_name, status, due_date, priority, file_data, file_name, assigned_to, assigned_by))
    conn.commit()

def get_tasks_from_db():
    """Retrieve all tasks from the database."""
    c.execute('SELECT * FROM tasks')
    return c.fetchall()

def update_task_in_db(task_id, status, due_date, priority):
    """Update an existing task in the database."""
    c.execute('''
        UPDATE tasks 
        SET status = ?, due_date = ?, priority = ?
        WHERE id = ?
    ''', (status, due_date, priority, task_id))
    conn.commit()

def delete_task_from_db(task_id):
    """Delete a task from the database."""
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()

def add_user_to_db(email, name):
    """Add a new user to the database."""
    c.execute('''
        INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)
    ''', (email, name))
    conn.commit()

def get_users_from_db():
    """Retrieve all users from the database."""
    c.execute('SELECT * FROM users')
    return c.fetchall()

def delete_user_from_db(email):
    """Delete a user from the database."""
    try:
        c.execute('SELECT COUNT(*) FROM users')
        user_count = c.fetchone()[0]

        # Ensure at least one user remains in the database
        if user_count > 1:
            c.execute('DELETE FROM users WHERE email = ?', (email,))
            conn.commit()
            return True
        else:
            st.error("Cannot delete the only remaining user. Please add another user before deleting the example user.")
            return False
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the user: {e}")
        return False

def send_email_confirmation(email, name):
    """Send a confirmation email to a new user."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "neslinnajeeboffice@gmail.com"  # Replace with your email
    sender_password = "bnob vrsk dinp miid"  # Replace with your app password

    subject = "Welcome to the Task Management App"
    body = f"Hi {name},\n\nYou have been added to the Task Management App.\n\nBest Regards,\nAdmin"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        st.success(f"Confirmation email sent to {email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Initialize the app layout
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Task Management", "Settings"])

if page == "Task Management":
    st.title("Task Management App")

    # Add task with file
    with st.form(key='task_form'):
        task_name = st.text_input("Task Name")
        status = st.selectbox("Status", ['To Do', 'In Progress', 'Completed'])
        due_date = st.date_input("Due Date", min_value=datetime.today())
        priority = st.selectbox("Priority", ['Low', 'Medium', 'High'])
        file = st.file_uploader("Upload File", type=['txt', 'pdf', 'jpg', 'png'])
        users = [user[1] for user in get_users_from_db()]  # Get list of user names
        assigned_to = st.selectbox("Assign To", users, key='assigned_to')
        assigned_by = st.selectbox("Assigned By", users, key='assigned_by')
        submit_button = st.form_submit_button("Add Task")
        if submit_button:
            if assigned_to and assigned_by:  # Ensure there are no empty fields
                file_data = file.read() if file else None

                # Debugging output
                st.write(f"Debug Info - Task Name: {task_name}, Status: {status}, Due Date: {due_date}, Priority: {priority}, Assigned To: {assigned_to}, Assigned By: {assigned_by}")

                add_task_to_db(task_name, status, due_date, priority, file_data, file.name if file else None, assigned_to, assigned_by)
                st.success(f"Task '{task_name}' added successfully!")
                st.experimental_rerun()
            else:
                st.error("Please select valid users for assignment.")

    # Display tasks
    tasks = get_tasks_from_db()
    if tasks:
        st.write("### Task List")
        for i, task in enumerate(tasks, start=1):
            # Correct order of unpacking based on schema
            task_id, task_name, status, due_date, priority, file_name, assigned_to, assigned_by, file_data = task


            with st.expander(f"Task {i}: {task_name}", expanded=True):
                st.write("Task ID:", task_id)
                st.write("Task Name:", task_name)
                st.write("Status:", status)
                st.write("Due Date:", due_date)
                st.write("Priority:", priority)
                st.write("Assigned To:", assigned_to)
                st.write("Assigned By:", assigned_by)
                if file_name:
                    st.write("File Name:", file_name)
                    if file_data:
                        st.download_button(
                            label="Download File",
                            data=file_data,
                            file_name=file_name,
                            mime="application/octet-stream"
                        )
                    else:
                        st.write("No file data available.")

                # Define columns for task controls
                col2, col3 = st.columns([2, 1])

                with col2:
                    # Status selection
                    new_status = st.selectbox(
                        "Status",
                        ['To Do', 'In Progress', 'Completed'],
                        key=f'status_{task_id}',
                        index=['To Do', 'In Progress', 'Completed'].index(status)
                    )
                    if new_status != status:
                        update_task_in_db(task_id, new_status, due_date, priority)
                        st.experimental_rerun()
                    status_colors = {
                        'To Do': 'red',
                        'In Progress': 'orange',
                        'Completed': 'green'
                    }
                    st.markdown(
                        f'<span style="color:{status_colors[status]};">{status}</span>',
                        unsafe_allow_html=True
                    )
                with col3:
                    delete_button = st.button("Delete Task", key=f'delete_button_{task_id}')
                    if delete_button:
                        delete_task_from_db(task_id)
                        st.success("Task deleted successfully!")
                        st.experimental_rerun()
    else:
        st.write("No tasks found.")

elif page == "Settings":
    st.title("Settings")

    # Add user
    with st.form(key='user_form'):
        st.write("### Add New User")
        new_user_email = st.text_input("User Email", key='user_email')
        new_user_name = st.text_input("User Name", key='user_name')
        add_user_button = st.form_submit_button("Add User")
        if add_user_button:
            if new_user_email and new_user_name:  # Ensure no empty fields
                add_user_to_db(new_user_email, new_user_name)
                send_email_confirmation(new_user_email, new_user_name)
                st.success(f"User '{new_user_name}' added successfully!")
                st.experimental_rerun()
            else:
                st.error("Please fill out all fields.")

    # List users
    users = get_users_from_db()
    if users:
        st.write("### User List")
        for i, user in enumerate(users, start=1):
            email, name = user
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i}. {name} ({email})**")
            with col2:
                delete_button = st.button(f"Delete User {i}", key=f'delete_user_{i}')
                if delete_button:
                    if delete_user_from_db(email):
                        st.success(f"User '{name}' deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to delete user '{name}'.")
    else:
        st.write("No users found.")

conn.close()
