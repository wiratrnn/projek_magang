import mysql.connector
from streamlit.delta_generator import DeltaGenerator
import hashlib

def _metric_card(self, title, value, icon="⭐", bg_color="#ffffff"):
    self.markdown(
        f"""
        <div style="
            background-color:{bg_color};
            padding:10px;
            border-radius:12px;
            color:white;
            height:80px;
            display:flex;
            align-items:center;
            justify-content:flex-start;
            border:3px solid black;
            margin-bottom:10px;
        ">
            <div style="font-size:30px; opacity:0.8;">
                {icon}
            </div>
            <div style="
                display:flex;
                flex-direction:column;
                align-items:flex-start;        
                align-items:center;
                width:100%;
            ">
                <div style="font-size:15px; font-weight:500; margin-top:5px;">{title}</div>
                <div style="font-size:30px; font-weight:bold;">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

DeltaGenerator.metric_card = _metric_card

def hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def connection():
    return mysql.connector.connect(
        host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
        user='3z6cRQ7E5WYFy8C.root',
        password='zSfk6X4v2VT53fQm',
        database='SIPENDEKAR',
        port=4000)

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

def execute_one(query, params):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount

def execute_all(query, params):
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(query, params)
            conn.commit()
            return cursor.rowcount

def sync_total(id_pegawai, id_periode):
    with connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT na.nilai, a.bobot, na.id_penilai
                FROM nilai_aspek na
                JOIN aspek a ON a.id_aspek = na.id_aspek
                WHERE na.id_pegawai=%s AND na.id_periode=%s
                """, (id_pegawai, id_periode))
            rows = cursor.fetchall()

            if not rows:
                return

            total = sum(r["nilai"] * r["bobot"] for r in rows)
            jml_penilai = len({r["id_penilai"] for r in rows})
            hasil = round((total / 100) / jml_penilai, 2)

            cursor.execute("""
                INSERT INTO nilai_total (id_pegawai,id_periode,nilai)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE nilai=VALUES(nilai)
                """, (id_pegawai, id_periode, hasil))

            conn.commit()
