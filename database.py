from pymongo import MongoClient
import streamlit as st

def get_database():
    """Connects to MongoDB (local or cloud) based on secrets.toml settings."""
    mongo_config = st.secrets["mongo"]

    use_cloud = True  # Change to False for local MongoDB

    if use_cloud:
        mongo_uri = mongo_config["cloud_uri"]  # No need to format
        db_name = mongo_config["cloud_db"]
        collection_name = mongo_config["cloud_collection"]
    else:
        mongo_uri = mongo_config["local_uri"]
        db_name = mongo_config["local_db"]
        collection_name = mongo_config["local_collection"]

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    return collection
