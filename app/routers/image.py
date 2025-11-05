from fastapi import APIRouter
from pydantic import BaseModel
from app.services.dalle_service import generate_image
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class ImageInput(BaseModel):
    text: str  # 이미지 생성용 텍스트 프롬프트

@router.post("/create")
async def create_image(data: ImageInput):
    """
    텍스트 프롬프트를 받아 이미지를 생성하고 URL 반환
    """
    try:
        # 이미지 생성
        image_url = generate_image(data.text)

        # 생성 실패 처리
        if not image_url:
            logging.error("이미지 생성 실패: URL이 반환되지 않음")
            return {"status": "error", "message": "이미지 생성 실패"}

        # 성공 로그
        logging.info(f"생성된 이미지 URL: {image_url}")

        # 결과 반환
        return {"status": "success", "image_url": image_url}

    except Exception as e:
        logging.error(f"이미지 생성 중 오류 발생: {e}")
        return {"status": "error", "message": str(e)}
