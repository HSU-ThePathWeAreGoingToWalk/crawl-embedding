import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

db = pymysql.connect(
    host=DB_HOST,
    user = DB_USER,
    password=DB_PASSWORD,
    database = DB_NAME
)
cursor = db.cursor()

# 현재 DB에서 가장 최근 공지가 실린 날짜 가져오기
def get_latest_date():
    cursor.execute("SELECT MAX(date) as latest_pub_date FROM notice")
    result = cursor.fetchone()
    latest_pub_date = result[0] if result[0] else datetime.min
    print(latest_pub_date)

    return latest_pub_date


# 현재 DB에서 standard(datetime) 이후의 공지만 필터링 (이후 임베딩 및 Pinecone에 저장)
# def filtering(standard):
    # 필터링 어떻게 하고 임베딩 어떻게 할지 고민하자