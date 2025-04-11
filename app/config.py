from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 임베딩 모델 설정
EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-large")

# Pinecone 벡터 DB 설정
INDEX_NAME = "goheung-notice"
DATABASE = PineconeVectorStore.from_existing_index(index_name=INDEX_NAME, embedding=EMBEDDING)