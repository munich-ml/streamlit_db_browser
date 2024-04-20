import streamlit as st
import os
from ruamel.yaml import YAML

st.header("Simple App", divider="green")
st.write("This is a dummy app for testing only!")

home_dir = os.path.expanduser("~")
secrets_path = os.path.join(home_dir, "py_app_exchange", "secrets.yaml")
if not os.path.exists(secrets_path):
    st.write(f"Error: secrets.yaml not found at {secrets_path}!")
    st.write(f"{os.getcwd()=}")
    st.write(f"{os.listdir(home_dir)=}")
else:    
    with open(secrets_path, "r") as file:
        secrets = YAML().load(file)
        st.write(f'secrets.yaml contains influx secrets {dict(secrets["influx"]).keys()}')