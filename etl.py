import pandas as pd
import json
from database import get_database
import streamlit as st

def load_csv(file_path):
    """Reads CSV and converts it to JSON format for MongoDB."""
    df = pd.read_csv(file_path)
    return json.loads(df.to_json(orient="records"))

def insert_data_to_mongo():
    """Loads data from CSV and inserts into MongoDB."""
    mongo_config = st.secrets["mongo"]
    source_path = mongo_config["source_path"]

    collection = get_database()
    data = load_csv(source_path)

    if data:
        collection.insert_many(data)
        st.success("Data inserted into MongoDB!")

if _name_ == "_main_":
    insert_data_to_mongo()
