import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from jose import jwt

# Set the page configuration as the first Streamlit command
st.set_page_config(
    layout="wide",
    page_title="Neslcom Analytics"  # This sets the browser tab title
)

# Auth0 application details
AUTH0_DOMAIN = 'dev-b7ps2b12l8twj4kx.us.auth0.com'
CLIENT_ID = 'wOCGlDZYxIk17PgOE3xJ2HH0r0uHRpQ2'
CLIENT_SECRET = 'gpQil0KlgZjwZfZI5gGFBD40aZ-FpHp17GNSiYfG9ipxSJXl9hMsqKLWTyS6mYXt'
REDIRECT_URI = 'https://app.neslcom.online/callback'  # E.g., https://app.neslcom.online/callback
PUBLIC_KEY_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

def get_auth_url():
    return f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid profile email"

def get_token(auth_code):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }
    token_res = requests.post(token_url, json=token_data)
    return token_res.json()

def get_user_info(access_token):
    user_url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_res = requests.get(user_url, headers=headers)
    return user_res.json()

def decode_jwt(token):
    response = requests.get(PUBLIC_KEY_URL)
    jwks = response.json()
    keys = {key['kid']: key for key in jwks['keys']}
    if 'kid' in jwt.get_unverified_header(token):
        key = keys[jwt.get_unverified_header(token)['kid']]
        return jwt.decode(token, key, algorithms=['RS256'], audience=CLIENT_ID)
    return None

# Authentication check
auth_code = st.experimental_get_query_params().get('code', [None])[0]
if auth_code:
    token_info = get_token(auth_code)
    access_token = token_info.get('access_token')

    # Decode and verify JWT
    user_info = decode_jwt(access_token)
    if user_info:
        st.title("Neslcom Data Dashboard")
        st.write(f"Hello, {user_info['name']}!")
        st.write(f"Email: {user_info['email']}")

        # Sample dataset URL
        sample_data_url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"

        # Sidebar for sample dataset option
        st.sidebar.header("Data Upload Options")
        if st.sidebar.button("Load Sample Dataset"):
            df = pd.read_csv(sample_data_url)
            st.success("Sample dataset loaded!")
        else:
            # File uploader for multiple files
            uploaded_files = st.file_uploader("Choose CSV file(s)", type=["csv"], accept_multiple_files=True)

            if uploaded_files:
                if len(uploaded_files) == 1:
                    # Single file uploaded
                    df = pd.read_csv(uploaded_files[0])
                    st.success(f"{uploaded_files[0].name} successfully uploaded!")
                else:
                    # Multiple files uploaded
                    dfs = []
                    for uploaded_file in uploaded_files:
                        # Display file size
                        file_size_kb = uploaded_file.size / 1024
                        st.sidebar.write(f"{uploaded_file.name} - {file_size_kb:.2f} KB")

                        df_temp = pd.read_csv(uploaded_file)
                        dfs.append(df_temp)

                    # Merge all uploaded files
                    df = pd.concat(dfs, ignore_index=True)
                    st.success(f"{len(uploaded_files)} file(s) successfully uploaded and merged!")

        # Check if data is loaded
        if 'df' in locals():
            st.sidebar.header("Filter Options")

            st.subheader("Data Preview")
            st.write(df.head())

            st.subheader("Data Summary")
            st.write(df.describe())

            st.subheader("Filter Data")
            columns = df.columns.tolist()

            filtered_df = df.copy()

            # Select columns to filter
            with st.sidebar.expander("Select Columns to Filter"):
                selected_columns = st.multiselect("Choose columns to apply filters", columns)

            # Apply filters for selected columns
            for column in selected_columns:
                with st.sidebar.expander(f"Filter {column}"):
                    if pd.api.types.is_numeric_dtype(df[column]):
                        min_val, max_val = st.slider(
                            f"Select range for {column}",
                            float(df[column].min()),
                            float(df[column].max()),
                            (float(df[column].min()), float(df[column].max()))
                        )
                        filtered_df = filtered_df[(filtered_df[column] >= min_val) & (filtered_df[column] <= max_val)]

                    elif pd.api.types.is_categorical_dtype(df[column]) or df[column].dtype == object:
                        # Add a search bar for categorical columns
                        unique_values = df[column].unique()
                        search_term = st.text_input(f"Search {column}")
                        filtered_values = [val for val in unique_values if search_term.lower() in str(val).lower()]
                        selected_values = st.multiselect(f"Select values for {column}", filtered_values,
                                                         default=filtered_values)
                        filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

                    elif pd.api.types.is_datetime64_any_dtype(df[column]):
                        # Add date range filter for datetime columns
                        date_range = st.date_input(f"Select date range for {column}", [df[column].min(), df[column].max()])
                        filtered_df = filtered_df[
                            df[column].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]

            st.write(filtered_df)

            st.subheader("Plot Data")
            x_column = st.selectbox("Select X-axis column", columns)
            y_column = st.selectbox("Select Y-axis column", columns)
            chart_type = st.selectbox("Select Chart Type",
                                      ["Line Chart", "Bar Chart", "Area Chart", "Scatter Plot", "Histogram"])

            # Initialize a placeholder for the plot
            plot_placeholder = st.empty()

            if st.button("Generate Plot"):
                if chart_type == "Line Chart":
                    fig = px.line(filtered_df, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
                elif chart_type == "Bar Chart":
                    fig = px.bar(filtered_df, x=x_column, y=y_column, title=f"{y_column} by {x_column}")
                elif chart_type == "Area Chart":
                    fig = px.area(filtered_df, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(filtered_df, x=x_column, y=y_column, title=f"{y_column} vs {x_column}")
                elif chart_type == "Histogram":
                    fig = px.histogram(filtered_df, x=y_column, nbins=10, title=f"Histogram of {y_column}")

                # Display plot
                plot_placeholder.plotly_chart(fig)

            # Button to download filtered data
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name='filtered_data.csv',
                mime='text/csv'
            )

        else:
            st.write("Waiting for file upload or sample dataset selection...")

    else:
        st.write("Invalid token or user information.")
        st.markdown(f"[Login with Auth0]({get_auth_url()})")
        st.stop()  # Stop further execution to prevent loading the app content

else:
    # Redirect to Auth0 login page if not authenticated
    st.markdown(f"[Login with Auth0]({get_auth_url()})")
    st.stop()  # Stop further execution to prevent loading the app content
