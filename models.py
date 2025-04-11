from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

# SQLAlchemy 모델 정의
class Notice(Base):
    __tablename__ = "notice"

    # 기본 키 및 필드 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    link = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    image = Column(Text, nullable=True)