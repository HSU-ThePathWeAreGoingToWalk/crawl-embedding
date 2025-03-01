import pymysql
import time
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

class Document:
    def __init__(self, page_content, metadata = None, id = None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
        self.id = id

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

#1. 테이블에서 데이터를 배열로 반환
def crawled_data_to_array():
    fetch_query = "SELECT id, title, link, content, date from notice"
    cursor.execute(fetch_query)
    rows = cursor.fetchall()
    return rows

#2. 메타데이터와 함께 임베딩 생성 및 저장
def store_array_to_vector_db():
    embedding = OpenAIEmbeddings(model = 'text-embedding-3-large')
    index_name = 'uljin-notice'

    rows = crawled_data_to_array()
    documents = []
    for id, title, link, content, pub_date in rows:
        #날짜를 타임스탬프로 변환
        date_object = datetime.strptime(str(pub_date), "%Y-%m-%d %H:%M:%S")
        unix_timestamp = int(time.mktime(date_object.replace(hour=0, minute=0, second=0, microsecond=0).timetuple()))

        #문서 내용 생성
        combined_content = f"Title: {title}\nLink: {link}\nContent: {content}"
        metadata = {
            'title' : title,
            'link' : link,
            'pub_date' : unix_timestamp
        }
        documents.append(Document(combined_content, metadata, id=str(id)))

    #문서를 Pinecone에 저장
    PineconeVectorStore.from_documents(documents, embedding, index_name  = index_name)

    print(f"{len(documents)}개의 문서가 Pinecone에 업로드되었습니다.")

store_array_to_vector_db()

cursor.close()
db.close()