import requests
from bs4 import BeautifulSoup
from models import Notice
from database import SessionLocal
from datetime import datetime

def crawl_new_notices(since_date: datetime):
    """
    기준일 이후의 공지사항만 크롤링하여 DB에 저장
    SQLAlchemy를 사용하여 데이터베이스에 저장
    DATETIME 타입에 맞게 'YYYY-MM-DD HH:MM:SS' 형식으로 날짜를 저장
    """
    session = SessionLocal()
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
            date_str = date_tag.text.replace("작성일 :", "").strip() if date_tag else None

            if date_str:
                try:
                    # 원래 형식은 "2025-03-19 10:31"이므로 datetime 객체로 파싱
                    notice_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    # DATETIME 컬럼에 맞게 시간까지 포함한 문자열로 포맷
                    formatted_date_str = notice_date.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print(f"날짜 파싱 실패: {date_str}")
                    continue

                if notice_date <= since_date:
                    print(f"기준일 이전 공지라서 무시됨: {date_str}")
                    continue
            else:
                print("작성일 없음, 무시")
                continue

            # 본문 내용 크롤링 (p 태그와 small 태그 포함)
            content_div = notice_soup.find("div", class_="bd_view_cont")
            content = ""
            if content_div:
                # <p> 태그 내용들을 줄바꿈(\n)으로 연결
                p_tags = content_div.find_all("p")
                content = "\n".join([p.get_text(separator="\n").strip() for p in p_tags if p.text.strip()])

                # <small> 태그 내용 추가 (존재할 경우)
                small_tag = content_div.find("small")
                if small_tag:
                    content = f"{small_tag.text.strip()}\n\n{content}"

            content = content.strip() if content else "내용 없음"

            # SQLAlchemy를 사용하여 공지사항 저장
            new_notice = Notice(title=title, content=content, image=img_src, date=formatted_date_str)
            session.add(new_notice)
            session.commit()

            print("\n")
            print(f"페이지 {page} - {i}번째 공지사항")
            print("URL:", link)
            print("제목:", title)
            print("이미지 링크:", img_src)
            print("작성일:", date_str)
            print(f"내용: {content[:200]}...")
            print("=" * 100)

    session.close()