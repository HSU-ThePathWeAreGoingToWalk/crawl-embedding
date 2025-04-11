from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# 데이터베이스 URL 생성
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 모델 클래스의 기본 클래스
Base = declarative_base()