# 🚀 2025 Cisco Innovation Challenge

## 📦 크롤링 및 임베딩 시스템 Repository
본 프로젝트는 **한성대학교 '우리가 걸어갈 길' 팀**이 진행한 **2025 Cisco Innovation Challenge** 참가작의 일부입니다.

<br>

## 📌 프로젝트 개요

> 이 시스템은 고흥 군청 공식 웹사이트의 공지사항의 자동 크롤링, 이미지 내 텍스트 추출 (OCR), <br>
>
> 그리고 임베딩 생성 및 벡터 데이터베이스 저장의 전 과정을 자동화하여, <br>
>
> 관리자 시스템에서 '업데이트' 버튼만 누르면 최신 공지 데이터가 자동으로 갱신되도록 구성되어 있습니다. <br>
>
> 관리자는 복잡한 수작업 없이도 최신 공지사항을 손쉽게 시스템에 반영할 수 있습니다. <br>

<br>

## 🛠️ 사용 기술 스택
- **Language**: Python 3.9 
- **Web Framework**: FastAPI 
- **ASGI Server**: Uvicorn 
- **Database**: MySQL, Pinecone (Vector DB) 
- **ORM**: SQLAlchemy 
- **OCR**: Apple Vision API (via `pyobjc-framework-Vision`)

<br>

## 🗂️ 프로젝트 구조

```bash
crawl-embedding/
│
├── app/                              # 주요 기능 디렉토리
│   ├── config.py                     # 환경 설정 파일
│   ├── crawl.py                      # 공지사항 크롤링 기능
│   ├── database.py                   # DB 연결 및 세션 관리
│   ├── embedding.py                  # 임베딩 및 벡터 DB 저장
│   ├── get_latest_notice_date.py     # 최신 공지사항 날짜 확인
│   ├── main.py                       # FastAPI 엔트리포인트
│   ├── models.py                     # SQLAlchemy 모델 정의
│   └── parse_images.py               # 이미지 OCR 및 텍스트 추출
│
├── .gitignore                        # Git 추적 제외 파일 목록
└── requirements.txt                  # 패키지 의존성 목록
```

<br>

## ✨ 주요 기능 소개
> #### 🔍 공지사항 크롤링 자동화
> - `get_latest_notice_date.py`: DB에 저장된 가장 최신 공지사항의 날짜를 확인합니다. 
> - `crawl.py`: 고흥 군청 공식 웹사이트에서 새로운 공지사항(제목, 내용, 날짜, 이미지 URL 등)을 크롤링합니다. 
> - 새로 수집된 공지사항 데이터를 MySQL 데이터베이스에 저장합니다.

> #### 🖼️ 이미지 기반 텍스트 처리 (OCR)
> - 이미지가 포함된 공지사항을 자동으로 식별합니다. 
> - 이미지 URL에서 이미지를 다운로드한 후, **Apple Vision API**을 사용해 텍스트를 추출합니다. 
> - 추출된 텍스트는 기존 공지사항 본문에 통합되어 저장됩니다.

> #### 🧠 텍스트 임베딩 및 벡터 저장
> - 텍스트 데이터(본문 + 이미지 텍스트)를 전처리한 후, **OpenAI API**를 사용하여 임베딩 벡터를 생성합니다. 
> - 생성된 벡터는 **Pinecone 벡터 DB**에 저장되며, 공지 ID, 날짜 등의 메타데이터와 함께 관리됩니다.

> #### 🔁 전체 파이프라인 자동화
> - 새로운 공지사항이 존재할 경우 아래 파이프라인이 자동으로 실행됩니다: <br>
>   공지사항 수집 → 이미지 OCR → 임베딩 → 벡터 DB 저장 → DB 상태 업데이트

> #### 🚀 API 연동 (FastAPI 기반)
> - 외부 관리자 시스템과의 연동을 위한 API 서버를 제공합니다. 
> - 관리자 페이지에서 '업데이트' 버튼 클릭 시 전체 파이프라인이 실행되도록 설계되어 있습니다.

<br>

## 📈 플로우 다이어그램
<img width="530" alt="Image" src="https://github.com/user-attachments/assets/967dfa53-3da3-4cb9-b3ac-6791af0add3a" />

<br>
<br>

## ⚙️ 설치 및 실행 방법
### 1. 가상 환경 설정
   
Python 3.9 버전을 사용하여 가상 환경을 생성합니다:

```bash
/opt/homebrew/opt/python@3.9/bin/python3.9 -m venv venv

```

> 위 명령어는 Homebrew로 Python 3.9를 설치한 macOS 환경을 기준으로 작성되었습니다.
>
> 일반적인 환경에서는 `python3.9 -m venv venv` 로 대체 가능합니다.
<br>

가상 환경을 활성화합니다:
   
```bash
source venv/bin/activate
```

<br>
 
### 2. 의존성 설치

패키지 캐시 없이 설치하려면 다음 명령어를 사용합니다:

```bash
pip install --no-cache-dir -r requirements.txt
```

<br>
 
### 3. 환경 변수 설정 (.env 파일)

프로젝트 루트 디렉토리에 .env 파일을 생성하고 아래 형식에 맞춰 정보를 입력하세요:

```env
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name

OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

> 주의: 이 파일은 민감한 정보를 포함하므로 .gitignore에 반드시 포함되어야 하며, 절대 커밋하지 않도록 주의하세요

<br>

###  4. 데이터베이스 설정
   
MySQL을 실행한 후, 터미널에서 아래 명령어로 데이터베이스를 생성합니다:
```sql
CREATE DATABASE your_database_name;
```

> your_database_name은 .env의 DB_NAME과 일치해야 합니다.

<br>
 
### 5. 서버 실행

FastAPI 서버를 실행합니다:

```bash
venv/bin/python -m uvicorn app.main:app --reload 
```

> 기본적으로 http://127.0.0.1:8000 에서 실행됩니다.

<br>

## 🚫 시스템 환경 제약
> 본 프로젝트는 **Apple의 Vision.framework**를 활용하는 관계로 **macOS**에서만 정상적으로 동작합니다.
> 
> Linux 또는 Windows에서는 Apple Vision API가 지원되지 않기 때문에,
> 
> 이미지 텍스트 추출 기능을 사용하려면 대체 OCR 솔루션(Tesseract 등)으로 커스터마이징이 필요합니다.

<br>


## ⁉️ 정보 수집을 위한 공식 문의 및 회신
##### 고흥군청 공지사항 크롤링 관련 민원 및 회신 내용
![Image](https://github.com/user-attachments/assets/c8f436d6-f72a-4a18-8c25-8835732185cf)

<br>

## 📄 라이선스

이 프로젝트는 **MIT 라이선스**를 따릅니다.
