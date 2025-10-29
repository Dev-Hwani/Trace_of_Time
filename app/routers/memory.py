from fastapi import APIRouter
from app.schemas.memory_schema import MemoryInput
from app.services.gpt_service import analyze_memory
from app.services.dalle_service import generate_image
from app.models.memory_model import save_memory, get_all_memories
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.post("/create")
async def create_memory(memory: MemoryInput):
    try:
        # GPT 분석
        gpt_result = analyze_memory(memory.text)

        # 이미지 생성
        image_url = generate_image(memory.text)

        # 이미지 URL 로그 출력
        logging.info(f"생성된 이미지 URL: {image_url}")

        # DB 저장
        memory_id = save_memory(memory.text, memory.date, gpt_result, image_url)

        return {
            "status": "success",
            "memory_id": memory_id,
            "memory_text": memory.text,
            "gpt_analysis": gpt_result,
            "image_url": image_url
        }
    except Exception as e:
        logging.error(f"Memory 생성 실패: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/all")
async def get_memories():
    """
    모든 기억을 시간순으로 조회
    """
    memories = get_all_memories()  # DB에서 date 기준으로 정렬된 리스트 반환
    return memories