import streamlit as st
import sqlite3

# Database connection
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# Function to check login credentials
def check_login(email, password):
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    return c.fetchone() is not None

# Function to add a new user
def signup(email, password):
    try:
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists

# Login Form
st.title("Login Page")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if check_login(email, password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.experimental_rerun()  # Redirect to main app
        else:
            st.error("Invalid email or password")

    st.subheader("Sign Up")
    new_email = st.text_input("New Email", placeholder="Email")
    new_password = st.text_input("New Password", type='password')

    if st.button("Sign Up"):
        if signup(new_email, new_password):
            st.success("User registered successfully")
        else:
            st.error("Email already exists. Try a different one.")

else:
    st.write("You are already logged in. Redirecting to the main application...")
    st.experimental_rerun()  # Redirect to main app
