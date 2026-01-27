import streamlit as st
import mysql.connector

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
        user='3z6cRQ7E5WYFy8C.root',
        password='SSDXhGgKq68XqT6N',
        database='projek_magang',
        port=4000)

def get_cursor():
    conn = get_connection()

    # cek apakah koneksi masih hidup
    try:
        conn.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        st.cache_resource.clear()
        conn = get_connection()

    return conn.cursor(dictionary=True)