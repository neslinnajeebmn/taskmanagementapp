import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Set the page configuration
st.set_page_config(
    page_title="Neslcom Calculator",
    page_icon="neslcom.png",
    layout="wide",
)

# Page title
st.title("Digital Marketing Calculator")

# Sidebar with interactive navigation and enhanced description
st.sidebar.title("Navigation")
st.sidebar.write("""
Welcome to the Digital Marketing Calculator.
Use the button below to navigate to the Neslcom Analytics dashboard.
""")

# Add custom HTML for redirect button with neutral color and white text
st.sidebar.markdown("""
    <style>
    .button {
        display: block;
        width: 100%;
        padding: 10px;
        font-size: 16px;
        text-align: center;
        background-color: #F5F5F5; /* Neutral gray color */
        color: #FFFFFF; /* White text color */
        border: none;
        border-radius: 5px;
        cursor: pointer;
        text-decoration: none;
    }
    .button:hover {
        background-color: #D3D3D3; /* Slightly darker gray for hover effect */
    }
    </style>
    <a href="https://app.neslcom.online" class="button" target="_blank">Go to Neslcom Analytics</a>
""", unsafe_allow_html=True)

# Currency selector
currency = st.selectbox(
    "Select Currency",
    [
        "USD", "EUR", "GBP", "INR", "AUD", "CAD", "JPY", "CNY", "CHF", "SEK", "NZD", "MXN", "SGD", "HKD", "NOK", "ZAR",
        "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD",
        "BND", "BOB", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CDF", "CLP", "COP", "CRC", "CUP", "CVE", "CZK", "DJF",
        "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "FJD", "FKP", "FOK", "GEL", "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ",
        "GYD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD", "KES", "KGS",
        "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA",
        "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MYR", "MZN", "NAD", "NGN", "NIO", "NPR", "OMR", "PAB",
        "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SHP",
        "SLE", "SOS", "SRD", "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TVD", "TZS",
        "UAH", "UGX", "UYU", "UZS", "VES", "VND", "VUV", "WST", "XAF", "XCD", "XOF", "XPF", "YER", "ZMW", "ZWL"
    ]
)

st.write("### Input your Ads metrics")

# Inputs for calculations
col1, col2 = st.columns(2)

with col1:
    ad_spend = st.number_input("Ad Spend", min_value=0.0, step=100.0)
    clicks = st.number_input("Clicks", min_value=0.0, step=100.0)
    conversions = st.number_input("Conversions", min_value=0.0, step=1.0)

with col2:
    conversion_value = st.number_input("Average Conversion Value", min_value=0.0, step=1.0)
    impressions = st.number_input("Impressions", min_value=0.0, step=100.0)

# Calculations
cpc = ad_spend / clicks if clicks else 0
cpa = ad_spend / conversions if conversions else 0
ctr = (clicks / impressions) * 100 if impressions else 0
roi = ((conversions * conversion_value) - ad_spend) / ad_spend * 100 if ad_spend else 0

# Display results with metrics
st.write("### Results")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Cost Per Click (CPC)", value=f"{currency} {cpc:.2f}")

with col2:
    st.metric(label="Cost Per Acquisition (CPA)", value=f"{currency} {cpa:.2f}")

with col3:
    st.metric(label="Click-Through Rate (CTR)", value=f"{ctr:.2f} %")

with col4:
    st.metric(label="Return on Investment (ROI)", value=f"{roi:.2f} %")

# Plot performance graph
st.write("### Performance Graph")

fig = go.Figure()

fig.add_trace(go.Bar(x=["CPC", "CPA", "CTR", "ROI"], y=[cpc, cpa, ctr, roi],
                     text=[f"{currency} {cpc:.2f}", f"{currency} {cpa:.2f}", f"{ctr:.2f} %", f"{roi:.2f} %"],
                     textposition='auto'))

fig.update_layout(title="Digital Marketing Metrics Performance",
                  xaxis_title="Metrics",
                  yaxis_title="Value")

st.plotly_chart(fig)

# Export metrics as CSV
def save_metrics_as_csv():
    try:
        data = {
            "Metric": ["Ad Spend", "Clicks", "Conversions", "Average Conversion Value", "Impressions",
                       "Cost Per Click (CPC)", "Cost Per Acquisition (CPA)", "Click-Through Rate (CTR)", "Return on Investment (ROI)"],
            "Value": [f"{currency} {ad_spend:.2f}", f"{clicks:.2f}", f"{conversions:.2f}",
                      f"{currency} {conversion_value:.2f}", f"{impressions:.2f}",
                      f"{currency} {cpc:.2f}", f"{currency} {cpa:.2f}", f"{ctr:.2f} %", f"{roi:.2f} %"]
        }
        df = pd.DataFrame(data)
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        return csv_bytes
    except Exception as e:
        st.error(f"An error occurred while creating the CSV: {e}")
        return None

# Download button for CSV
csv_bytes = save_metrics_as_csv()
if csv_bytes:
    st.download_button(
        label="Download Metrics as CSV",
        data=csv_bytes,
        file_name="digital_marketing_calculator_results.csv",
        mime="text/csv"
    )

# Make the interface more attractive with a success message
st.success(
    "Calculations are based on the inputs provided. Adjust the values to see how your metrics change and download the results as CSV!"
)
