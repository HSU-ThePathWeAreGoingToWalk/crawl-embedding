import requests
import io
import objc
from PIL import Image
import Vision
from typing import List, Tuple
from datetime import datetime
from models import Notice
from database import SessionLocal

# 이미지 처리 및 데이터베이스 작업을 위한 함수 정의
def pil2buf(pil_image: Image.Image):
    """PIL 이미지를 버퍼로 변환"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()

def load_image_from_url(url: str) -> Image.Image:
    """URL에서 이미지를 로드하여 PIL 형식으로 변환"""
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        raise Exception(f"이미지를 {url}에서 가져오는데 실패했습니다.")

def text_from_image(
    image, recognition_level="accurate", language_preference=None, confidence_threshold=0.0
) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
    """Apple의 Vision 프레임워크를 사용하여 이미지에서 텍스트 추출"""
    if not isinstance(image, Image.Image):
        raise ValueError("잘못된 이미지 형식입니다. 이미지는 PIL 이미지여야 합니다.")

    if recognition_level not in {"accurate", "fast"}:
        raise ValueError("잘못된 인식 수준입니다. 'accurate' 또는 'fast'여야 합니다.")

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError("언어 설정은 리스트여야 합니다.")

    with objc.autorelease_pool():
        req = Vision.VNRecognizeTextRequest.alloc().init()
        req.setRecognitionLevel_(1 if recognition_level == "fast" else 0)

        if language_preference is not None:
            available_languages = req.supportedRecognitionLanguagesAndReturnError_(None)[0]
            if not set(language_preference).issubset(set(available_languages)):
                raise ValueError(
                    f"잘못된 언어 설정입니다. {available_languages}의 부분집합이어야 합니다."
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
    session = SessionLocal()
    # 기준일 이후의, 이미지가 있는 공지사항 조회
    image_rows = session.query(Notice).filter(Notice.image.isnot(None), Notice.date > since_date).all()

    if not image_rows:
        print("이미지를 찾을 수 없습니다.")
    else:
        for notice in image_rows:
            try:
                # 이미지 다운로드 및 PIL 이미지로 변환
                image = load_image_from_url(notice.image)

                # OCR 처리
                recognized_text = text_from_image(
                    image,
                    recognition_level="accurate",
                    language_preference=["ko-KR"],
                    confidence_threshold=0.8
                )
                extracted_text = " ".join([text for text, _, _ in recognized_text])

                # 기존 content와 합치기
                if notice.content:
                    new_content = f"{notice.content} {extracted_text}"
                else:
                    new_content = extracted_text

                print("\n")
                print(f"ID {notice.id}에 대한 추출된 텍스트: {extracted_text}")
                
                # DB 업데이트 (기존 content에 덧붙이기)
                notice.content = new_content
                session.commit()
                print(f"ID {notice.id}의 내용이 업데이트되었습니다.")
                print("=" * 100)

            except requests.exceptions.RequestException as e:
                print(f"ID {notice.id}의 이미지 다운로드 실패: {e}")
            except Exception as e:
                print(f"ID {notice.id}에 대한 오류: {e}")

    session.close()