import streamlit as st
import requests

# Django API URL
DJANGO_API_URL = "http://127.0.0.1:8000/api/data"

st.title("Streamlit + Django Integration")

# API에서 데이터 가져오기
response = requests.get(DJANGO_API_URL)
if response.status_code == 200:
    data = response.json()
    st.write(f"**Message from Django:** {data['message']}")
    st.write(f"**Count Value:** {data['count']}")
else:
    st.error("Failed to fetch data from Django API")