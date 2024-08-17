import streamlit as st
import sqlite3

# Database connection
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# Function to check login credentials
def check_login(username, password):
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return c.fetchone() is not None

# Function to add a new user
def signup(username, password):
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

# Login Form
st.title("Login Page")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()  # Redirect to main app
        else:
            st.error("Invalid username or password")

    st.subheader("Sign Up")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type='password')

    if st.button("Sign Up"):
        try:
            signup(new_username, new_password)
            st.success("User registered successfully")
        except Exception as e:
            st.error(f"Error registering user: {e}")

else:
    st.write("You are already logged in. Redirecting to the main application...")
    st.experimental_rerun()  # Redirect to main app
