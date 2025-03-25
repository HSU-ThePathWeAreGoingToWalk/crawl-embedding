import pymysql  # pymysql로 변경
import requests
import io
import objc
from PIL import Image
import Vision
from typing import List, Tuple
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def pil2buf(pil_image: Image.Image):
    """Convert PIL image to buffer"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()

def load_image_from_url(url: str) -> Image.Image:
    """Load image from a URL into PIL format"""
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        raise Exception(f"Failed to retrieve image from {url}")

def text_from_image(
    image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """Extract text from image using Apple's Vision framework."""
    if not isinstance(image, Image.Image):
        raise ValueError("Invalid image format. Image must be a PIL image.")

    if recognition_level not in {"accurate", "fast"}:
        raise ValueError("Invalid recognition level. Must be 'accurate' or 'fast'.")

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError("Language preference must be a list.")

    with objc.autorelease_pool():
        req = Vision.VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLevel_(1 if recognition_level == "fast" else 0)

        if language_preference is not None:
            available_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]
            if not set(language_preference).issubset(set(available_languages)):
                raise ValueError(
                    f"Invalid language preference. Must be a subset of {available_languages}."
                )
            req.setRecognitionLanguages_(language_preference)

        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
            pil2buf(image), None
        )

        success = handler.performRequests_error_([req], None)
        res = []
        if success:
            for result in req.results():
                confidence = result.confidence()
                if confidence >= confidence_threshold:
                    bbox = result.boundingBox()
                    x, y = bbox.origin.x, bbox.origin.y
                    w, h = bbox.size.width, bbox.size.height
                    res.append((result.text(), confidence, (x, y, w, h)))
            
        return res


def update_notice_with_image_text(since_date: datetime):
    """
    DB에 저장된 notice 테이블에서 image URL이 존재하는 레코드를 조회하고
    해당 이미지의 OCR 텍스트를 기존 content 필드에 추가하여 업데이트 함
    """

    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # 기준일 이후의, 이미지가 있는 공지사항 조회
    cursor.execute(
        "SELECT id, image, content, date FROM notice WHERE image IS NOT NULL AND date > %s",
        (since_date)
    )
    image_rows = cursor.fetchall()

    if not image_rows:
        print("No images found.")
    else:
        for row in image_rows:
            id, image_url, existing_content, _ = row
            try:
                # 이미지 다운로드 및 PIL 이미지로 변환
                image = load_image_from_url(image_url)

                # OCR 처리
                recognized_text = text_from_image(
                    image,
                    recognition_level="accurate",
                    language_preference=["ko-KR"],
                    confidence_threshold=0.8
                )
                extracted_text = " ".join([text for text, _, _ in recognized_text])

                # 기존 content와 합치기
                if existing_content:
                    new_content = f"{existing_content} {extracted_text}"
                else:
                    new_content = extracted_text

                print("\n")
                print(f"Extracted text for ID {id}: {extracted_text}")
                # DB 업데이트 (기존 content에 덧붙이기)
                cursor.execute(
                    "UPDATE notice SET content = CONCAT(content, %s) WHERE id = %s",
                    (f" {extracted_text.strip()}", id)
                )
                db.commit()
                print(f"Updated content for ID {id}")
                print("=" * 100)

            except requests.exceptions.RequestException as e:
                print(f"Failed to download image for ID {id}: {e}")
            except Exception as e:
                print(f"Error for ID {id}: {e}")

    cursor.close()
    db.close()

