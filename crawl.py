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

def crawl_new_notices(last_date=None):

    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # 요청할 URL (실제 페이지 URL을 입력해야 함)
    base_url = "https://www.uljin.go.kr"  # 실제 URL로 변경 필요
    board_url = "https://www.uljin.go.kr/board/list.uljin?boardId=BBS_NOTICE_UJ&menuCd=DOM_000000103002001000&orderBy=REGISTER_DATE%20DESC&paging=ok&startPage="

    # <ul class="bbs_list"> 내부의 <li> 하위 <a> 태그에서 href 가져오기
    for page in range(1,3):
        url = board_url + str(page)
        print(url)
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공했는지 확인
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for li in soup.select("ul.bbs_list li a"):
            link = li.get("href")
            if link:
                if link.startswith("/"):
                    link = base_url + link
                links.append(link)

        # 각 공지사항 페이지에서 데이터 크롤링
        for i, link in enumerate(links, 1):

            notice_response = requests.get(link)
            notice_response.raise_for_status()
            notice_soup = BeautifulSoup(notice_response.text, "html.parser")

            title_tag = notice_soup.find("h4")
            title = title_tag.text.strip() if title_tag else "제목 없음"

            # 작성일 크롤링
            date_tag = notice_soup.find("th", string="작성일")
            date = date_tag.find_next("td").text.strip() if date_tag else "N/A"

            # 이미지 src 크롤링
            img_tag = notice_soup.find("td", class_="bbs_content").find("img") if notice_soup.find("td",class_="bbs_content") else None
            img_src = base_url + img_tag["src"] if img_tag else None

            # 내용 크롤링 (p 태그 내용 추출)
            content_tags = notice_soup.find("td", class_="bbs_content").find_all("p") if notice_soup.find("td", class_="bbs_content") else []
            content = "\n".join([p.text.strip() for p in content_tags]) if content_tags else "내용 없음"

            # MySQL 저장
            sql = "INSERT INTO notice (title, link, content, image, date) VALUES (%s, %s, %s, %s, %s)"
            val = (title, link, content, img_src, date)
            cursor.execute(sql, val)
            db.commit()

            # 결과 출력
            print(f"페이지 {page} - {i}번째 공지사항")
            # print("URL:", link)
            # print("제목:", title)
            print("작성일:", date)
            # print("이미지 링크:", img_src)
            # print(f"내용: {content[:100]}...")
            # print("=" * 100)
