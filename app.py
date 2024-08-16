import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page configuration
st.set_page_config(
    layout="wide",
    page_title="Neslcom Analytics"  # Customize the browser tab title
)

st.title("Neslcom Analytics")

# Inject custom HTML to modify meta title and metadata
st.markdown("""
    <style>
        .css-18e3th9 {visibility: hidden;}
    </style>
    <script>
        const meta = document.createElement('meta');
        meta.name = 'Neslcom Analytics';
        meta.content = 'Unlock powerful data insights with Neslcom Analytics. Easily upload, filter, and visualize your data for actionable results. Perfect for businesses seeking streamlined data analysis and decision-making.';
        document.getElementsByTagName('head')[0].appendChild(meta);

        document.title = 'Neslcom Analytics';
    </script>
    """, unsafe_allow_html=True)

# Initialize session state for storing the dataset
if 'df' not in st.session_state:
    st.session_state.df = None

# Sample dataset URL
sample_data_url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"

# Sidebar for sample dataset option
st.sidebar.header("Data Upload Options")
if st.sidebar.button("Load Sample Dataset"):
    try:
        df = pd.read_csv(sample_data_url)
        st.session_state.df = df  # Store in session state
        st.success("Sample dataset loaded!")
    except Exception as e:
        st.error(f"Error loading sample dataset: {e}")
else:
    # File uploader for multiple files
    uploaded_files = st.file_uploader("Choose CSV file(s)", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        dfs = []
        for uploaded_file in uploaded_files:
            try:
                df_temp = pd.read_csv(uploaded_file)
                dfs.append(df_temp)
                st.success(f"{uploaded_file.name} successfully uploaded!")
            except Exception as e:
                st.error(f"Error loading file {uploaded_file.name}: {e}")

        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            st.session_state.df = df  # Store in session state
        else:
            st.session_state.df = None
    else:
        st.session_state.df = None

# Check if data is loaded
if st.session_state.df is not None and not st.session_state.df.empty:
    st.sidebar.header("Filter Options")

    df = st.session_state.df  # Load the dataset from session state

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
    try:
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
                    unique_values = df[column].unique()
                    search_term = st.text_input(f"Search {column}")
                    filtered_values = [val for val in unique_values if search_term.lower() in str(val).lower()]
                    selected_values = st.multiselect(f"Select values for {column}", filtered_values,
                                                     default=filtered_values)
                    filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    date_range = st.date_input(f"Select date range for {column}", [df[column].min(), df[column].max()])
                    filtered_df = filtered_df[
                        df[column].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))]
    except Exception as e:
        st.error(f"Error applying filters: {e}")

    st.write(filtered_df)

    st.subheader("Plot Data")
    x_column = st.selectbox("Select X-axis column", columns)
    y_column = st.selectbox("Select Y-axis column", columns)
    chart_type = st.selectbox("Select Chart Type",
                              ["Line Chart", "Bar Chart", "Area Chart", "Scatter Plot", "Histogram"])

    # Initialize a placeholder for the plot
    plot_placeholder = st.empty()

    try:
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
    except Exception as e:
        st.error(f"Error generating plot: {e}")

    # Button to download filtered data
    try:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv'
        )
    except Exception as e:
        st.error(f"Error generating CSV download: {e}")

else:
    st.write("Waiting for file upload or sample dataset selection...")

