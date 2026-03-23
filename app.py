import plotly.express as px

def show_dashboard():
    conn = sqlite3.connect('churn_data.db')
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()

    if not df.empty:
        st.header("📈 Real-Time Churn Analytics")
        
        # Row 1: Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Predictions", len(df))
        col2.metric("At Risk Customers", len(df[df['Prediction'] == 1]))
        avg_risk = df['Probability'].mean()
        col3.metric("Avg Churn Risk", f"{avg_risk:.1%}")

        # Row 2: Charts
        c1, c2 = st.columns(2)
        
        with c1:
            # Donut Chart: Churn by Contract
            fig1 = px.pie(df, names='Contract', title='Risk by Contract Type', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            # Bar Chart: Churn by Gender
            fig2 = px.histogram(df, x="gender", color="Prediction", 
                                 title="Churn Count by Gender", barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data in database yet. Make a prediction to see charts!")







# --- DATABASE FUNCTIONS ---
def save_to_sql(df):
    conn = sqlite3.connect('churn_data.db')
    df.to_sql('predictions', conn, if_exists='append', index=False)
    conn.close()

def reset_database():
    conn = sqlite3.connect('churn_data.db')
    cursor = conn.cursor()
    # This deletes the table but keeps the file
    cursor.execute("DROP TABLE IF EXISTS predictions")
    conn.commit() # <--- Fixed: Changed 'connection' to 'conn'
    conn.close()











import sqlite3
import pandas as pd

def save_to_sql(df):
    # Creates/Connects to 'churn_data.db' in your project folder
    conn = sqlite3.connect('churn_data.db')
    # 'append' adds new rows without deleting old ones
    df.to_sql('predictions', conn, if_exists='append', index=False)
    conn.close()

import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np
import sqlite3

# --- STEP 1: DEFINE ALL FUNCTIONS FIRST (AT THE TOP) ---
def encode(value):
    mapping = {
        "No": 0, "Yes": 1, "Female": 0, "Male": 1, 
        "No phone service": 0, "No internet service": 0,
        "DSL": 0, "Fiber optic": 1, "Month-to-month": 0, 
        "One year": 1, "Two year": 2, "Electronic check": 2, 
        "Mailed check": 3, "Bank transfer": 0, "Credit card": 1
    }
    if isinstance(value, (int, float)):
        return value
    return mapping.get(value, 0)

def save_to_sql(df):
    conn = sqlite3.connect('churn_data.db')
    df.to_sql('predictions', conn, if_exists='append', index=False)
    conn.close()

# --- STEP 2: LOAD MODELS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "models", "model.pkl")
scaler_path = os.path.join(BASE_DIR, "models", "scaler.pkl")

try:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    st.success("✅ Model and Scaler Loaded Successfully!")
except Exception as e:
    st.error(f"❌ Error loading models: {e}")
    st.stop()

# --- STEP 3: INDIVIDUAL PREDICTION UI ---
st.title("📊 Customer Churn Prediction")
col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Gender", ["Female", "Male"])
    senior = st.selectbox("Is Senior Citizen?", [0, 1])
    partner = st.selectbox("Has Partner?", ["No", "Yes"])
    dependents = st.selectbox("Has Dependents?", ["No", "Yes"])
    tenure = st.slider("Tenure (Months)", 0, 72, 12)
    phone = st.selectbox("Phone Service", ["No", "Yes"])
    multiple = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
    internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])

with col2:
    backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
    protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
    support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
    tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
    movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    paperless = st.selectbox("Paperless Billing", ["No", "Yes"])
    payment = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer", "Credit card"])
    monthly = st.number_input("Monthly Charges ($)", 0.0, 200.0, 65.0)
    total = st.number_input("Total Charges ($)", 0.0, 10000.0, 500.0)

if st.button("Calculate Individual Churn Risk"):
    input_data = np.array([[
        encode(gender), senior, encode(partner), encode(dependents),
        tenure, encode(phone), encode(multiple), encode(internet),
        encode(security), encode(backup), encode(protection), encode(support),
        encode(tv), encode(movies), encode(contract), encode(paperless),
        encode(payment), monthly, total
    ]])
    
    scaled_data = scaler.transform(input_data)
    prob = float(model.predict_proba(scaled_data)[:, 1][0])
    prediction = 1 if prob > 0.5 else 0

    # Save individual record
    record = pd.DataFrame(input_data, columns=[
        "gender", "SeniorCitizen", "Partner", "Dependents", "tenure", 
        "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", 
        "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", 
        "StreamingMovies", "Contract", "PaperlessBilling", 
        "PaymentMethod", "MonthlyCharges", "TotalCharges"
    ])
    record['Probability'] = prob
    record['Prediction'] = prediction
    record['Timestamp'] = pd.Timestamp.now()
    save_to_sql(record)

    if prediction == 1:
        st.error(f"### ⚠️ High Risk: {prob:.1%} chance of leaving.")
    else:
        st.success(f"### ✅ Low Risk: {prob:.1%} chance of staying.")

# --- STEP 4: BULK PREDICTION UI ---
st.divider()
st.header("📂 Bulk Prediction (Upload CSV)")
uploaded_file = st.file_uploader("Upload your customer data CSV", type=["csv"])

if uploaded_file is not None:
    df_bulk = pd.read_csv(uploaded_file)
    st.write("Preview:", df_bulk.head())

    if st.button("Run Bulk Prediction"):
        processed_df = df_bulk.copy()
        # Now 'encode' is defined at the top, so this will work!
        for col in processed_df.select_dtypes(include=['object']).columns:
            processed_df[col] = processed_df[col].apply(encode)

        scaled_bulk = scaler.transform(processed_df)
        probs = model.predict_proba(scaled_bulk)[:, 1]
        
        df_bulk['Churn_Probability'] = [f"{p:.1%}" for p in probs]
        df_bulk['Churn_Prediction'] = ["Will Leave" if p > 0.5 else "Will Stay" for p in probs]
        df_bulk['Timestamp'] = pd.Timestamp.now()

        st.success("✅ Bulk Prediction Complete!")
        st.dataframe(df_bulk)
        save_to_sql(df_bulk)




import streamlit.components.v1 as components
components.iframe("YOUR_POWER_BI_EMBED_LINK_HERE", height=600)




st.divider()
if st.button("📊 Generate/Refresh Dashboard"):
    show_dashboard()



# --- SIDEBAR SETTINGS ---
st.sidebar.divider()
st.sidebar.warning("⚠️ Dangerous Area")
if st.sidebar.button("🗑️ Reset All Data"):
    reset_database()
    st.sidebar.success("Database Cleared! Refreshing...")
    # This automatically refreshes the app so the charts disappear
    st.rerun()
