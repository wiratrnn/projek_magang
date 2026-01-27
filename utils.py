import streamlit as st
import mysql.connector

def connection():
    return mysql.connector.connect(
        host=st.secrets['host'],
        user=st.secrets['user'],
        password=st.secrets['password'],
        database=st.secrets['database'],
        port=st.secrets['port'])

def fetch_one(query, params=None):
    with connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

def fetch_all(query, params=None):
    with connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

def execute(query, params=None):
    """
    Untuk INSERT / UPDATE / DELETE
    """
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
