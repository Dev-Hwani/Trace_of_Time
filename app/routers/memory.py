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
    """
    기억 생성: GPT 분석, 이미지 생성 후 DB 저장
    """
    try:
        logging.info(f"Memory 생성 요청: text='{memory.text[:30]}...' date='{memory.date}'")

        # GPT 분석
        try:
            gpt_result = analyze_memory(memory.text)
            logging.info(f"GPT 분석 완료: {gpt_result}")
        except Exception as gpt_err:
            logging.error(f"GPT 분석 실패: {gpt_err}")
            return {"status": "error", "message": "GPT 분석 실패"}

        # 이미지 생성
        try:
            image_url = generate_image(memory.text)
            logging.info(f"이미지 생성 완료: {image_url}")
        except Exception as img_err:
            logging.error(f"이미지 생성 실패: {img_err}")
            image_url = None  # 이미지 생성 실패 시 None 처리

        # DB 저장
        try:
            memory_id = save_memory(memory.text, memory.date, gpt_result, image_url)
            if memory_id is None:
                logging.error("Memory DB 저장 실패")
                return {"status": "error", "message": "DB 저장 실패"}
            logging.info(f"Memory DB 저장 완료 (ID: {memory_id})")
        except Exception as db_err:
            logging.error(f"Memory DB 저장 중 예외 발생: {db_err}")
            return {"status": "error", "message": "DB 저장 중 오류 발생"}

        return {
            "status": "success",
            "memory_id": memory_id,
            "memory_text": memory.text,
            "gpt_analysis": gpt_result,
            "image_url": image_url
        }

    except Exception as e:
        logging.error(f"Memory 생성 실패: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.get("/all")
async def get_memories():
    """
    모든 기억을 시간순으로 조회
    """
    try:
        memories = get_all_memories()
        logging.info(f"총 {len(memories)}개의 기억 조회 성공")
        return memories
    except Exception as e:
        logging.error(f"기억 조회 실패: {e}", exc_info=True)
        return {"status": "error", "message": "기억 조회 중 오류 발생"}

