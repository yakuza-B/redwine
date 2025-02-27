import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Function to connect to MongoDB
@st.cache_resource
def get_database():
    """Connects to MongoDB using Streamlit Secrets."""
    try:
        mongo_config = st.secrets["mongo"]  # Load secrets
        mongo_uri = mongo_config.get("cloud_uri", "")  # Ensure key exists
        db_name = mongo_config.get("cloud_db", "")
        collection_name = mongo_config.get("cloud_collection", "")

        if not mongo_uri or not db_name or not collection_name:
            st.error("⚠️ MongoDB configuration is missing. Check `.streamlit/secrets.toml`.")
            st.stop()

        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db[collection_name]

    except KeyError as e:
        st.error(f"⚠️ Missing key: {e}. Ensure `.streamlit/secrets.toml` has the correct structure.")
        st.stop()

# Initialize database connection
collection = get_database()

# Streamlit App UI
st.title("🍷 Wine Quality Database")

# --- Display Wine Data ---
st.subheader("📊 Wine Data Overview")
try:
    data = list(collection.find({}, {"_id": 0}))  # Fetch data (exclude MongoDB ID)
    
    # Filter out empty values
    filtered_data = [entry for entry in data if any(value not in [None, "", "N/A"] for value in entry.values())]

    if filtered_data:
        df = pd.DataFrame(filtered_data).drop_duplicates().fillna("N/A")
        with st.expander("🔍 Click to View Wine Data Table"):
            st.dataframe(df, width=800)
    else:
        st.warning("⚠️ No valid data found in MongoDB.")
except Exception as e:
    st.error(f"⚠️ Database Error: {e}")

# --- Insert New Data ---
st.subheader("➕ Add New Wine Data")

with st.form("insert_form"):
    col1, col2 = st.columns(2)

    with col1:
        fixed_acidity = st.number_input("Fixed Acidity", min_value=0.0, step=0.1)
        volatile_acidity = st.number_input("Volatile Acidity", min_value=0.0, step=0.01)
        citric_acid = st.number_input("Citric Acid", min_value=0.0, step=0.01)

    with col2:
        residual_sugar = st.number_input("Residual Sugar", min_value=0.0, step=0.1)
        chlorides = st.number_input("Chlorides", min_value=0.0, step=0.001)
        alcohol = st.number_input("Alcohol (%)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("📥 Submit Wine Data")

    if submitted:
        new_entry = {
            "fixed_acidity": fixed_acidity,
            "volatile_acidity": volatile_acidity,
            "citric_acid": citric_acid,
            "residual_sugar": residual_sugar,
            "chlorides": chlorides,
            "alcohol": alcohol,
        }

        # Prevent duplicate insertion
        if not collection.find_one(new_entry):
            collection.insert_one(new_entry)
            st.success("✅ New wine data added!")
            st.rerun()
        else:
            st.error("⚠️ Duplicate entry! Data already exists.")

