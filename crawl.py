import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pymysql

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

db = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = db.cursor()

base_url = "https://www.goheung.go.kr"
board_url = "https://www.goheung.go.kr/boardList.do?pageId=www96&boardId=BD_00018&movePage="

# 2페이지까지만 크롤링
for page in range(1, 3):
    url = board_url + str(page)
    print(f"페이지 크롤링: {url}")

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a_tag in soup.select(".bd_list_body .subject a"):
        link = a_tag.get("href")
        if link and link.startswith("/boardView.do"):
            full_link = base_url + link
            links.append(full_link)
            print(f"공지사항 링크: {full_link}")

    # 개별 공지사항 페이지 크롤링
    for i, link in enumerate(links, 1):
        notice_response = requests.get(link)
        notice_response.raise_for_status()
        notice_soup = BeautifulSoup(notice_response.text, "html.parser")

        # 제목 크롤링
        title_tag = notice_soup.find("h4")
        title = title_tag.text.strip() if title_tag else "제목 없음"

        # 이미지 크롤링
        img_tag = notice_soup.select_one(".view_img img")
        img_src = base_url + img_tag["src"] if img_tag else None

        # 작성일 크롤링
        date_tag = notice_soup.select_one(".bd_view_top p span:nth-of-type(2)")
        date = date_tag.text.replace("작성일 :", "").strip() if date_tag else "작성일 없음"

        # 본문 내용 크롤링 (p 태그 + small 태그 포함)
        content_div = notice_soup.find("div", class_="bd_view_cont")
        content = ""

        if content_div:
            # <p> 태그 내용 가져오기 (줄바꿈을 '\n'으로 변환)
            p_tags = content_div.find_all("p")
            content = "\n".join([p.get_text(separator="\n").strip() for p in p_tags if p.text.strip()])

            # <small> 태그 내용 추가
            small_tag = content_div.find("small")
            if small_tag:
                content = f"{small_tag.text.strip()}\n\n{content}"

        content = content.strip() if content else "내용 없음"

        # MySQL 저장
        sql = "INSERT INTO notice (title, content, image, date) VALUES (%s, %s, %s, %s)"
        val = (title, content, img_src, date)
        cursor.execute(sql, val)
        db.commit()

        # 결과 출력
        print("\n")
        print(f"페이지 {page} - {i}번째 공지사항")
        print("URL:", link)
        print("제목:", title)
        print("이미지 링크:", img_src)
        print("작성일:", date)
        print(f"내용: {content[:200]}...")
        print("=" * 100)

cursor.close()
db.close()
