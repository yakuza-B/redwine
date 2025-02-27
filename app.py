import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Function to connect to MongoDB
def get_database():
    """Connects to MongoDB using Streamlit Secrets."""
    mongo_config = st.secrets["mongo"]
    mongo_uri = mongo_config["cloud_uri"]
    db_name = mongo_config["cloud_db"]
    collection_name = mongo_config["cloud_collection"]

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    return collection

# Initialize database connection
collection = get_database()

# Streamlit App UI
st.title("🍷 Wine Quality Database")

# --- Display Wine Data ---
st.subheader("📊 Wine Data Overview")
data = list(collection.find({}, {"_id": 0}))  # Fetch data (exclude MongoDB ID)

# Remove entries where all values are None, empty, or "N/A"
filtered_data = [entry for entry in data if any(value not in [None, "", "N/A"] for value in entry.values())]

if filtered_data:
    df = pd.DataFrame(filtered_data)
    
    # Remove duplicate rows
    df = df.drop_duplicates()

    # Replace None values with "N/A"
    df.fillna("N/A", inplace=True)

    # Display table in an expandable section
    with st.expander("🔍 Click to View Wine Data Table"):
        st.dataframe(df, width=800)
else:
    st.warning("No valid data found in MongoDB.")

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
    
    st.markdown("---")  # Adds a separator for better UI
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
            collection.insert_one(new_entry)  # Insert into MongoDB
            st.success("✅ New wine data added!")
            st.rerun()  # Refresh the app
        else:
            st.error("⚠️ Duplicate entry! Data already exists.")
