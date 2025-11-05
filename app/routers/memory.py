from fastapi import APIRouter, HTTPException
from app.schemas.memory_schema import MemoryInput, MemoryUpdate
from app.services.gpt_service import analyze_memory, client
from app.services.dalle_service import generate_image
from app.models.memory_model import (
    save_memory,
    get_all_memories,
    update_memory,
    delete_memory
)
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

# memory 생성 기능
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
            image_val = gpt_result.get("이미지", memory.text)
            emotion_val = gpt_result.get("감정", "")
            era_val = gpt_result.get("시대", "")
            combined_prompt = f"{image_val} {emotion_val} {era_val}".strip() or memory.text
            image_url = generate_image(combined_prompt)
            logging.info(f"이미지 생성 완료: {image_url}")
        except Exception as img_err:
            logging.error(f"이미지 생성 실패: {img_err}")
            raise HTTPException(status_code=500, detail="이미지 생성 실패")

        # DB 저장
        memory_id = save_memory(memory.text, memory.date, gpt_result, image_url)
        if memory_id is None:
            logging.error("Memory DB 저장 실패")
            return {"status": "error", "message": "DB 저장 실패"}

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

# memory 전체 조회 기능
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


# memory 수정 기능
@router.put("/{memory_id}")
async def update_memory_item(memory_id: int, memory_update: MemoryUpdate):
    """
    특정 기억 수정 (텍스트, 날짜, 분석, 이미지 자동 재생성)
    """
    try:
        # Step 1️⃣ 텍스트 기반 새 이미지 생성
        prompt = f"{memory_update.date}의 기억: {memory_update.text}"
        logging.info(f"새 이미지 생성 중... (프롬프트: {prompt})")

        image_response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        new_image_url = image_response.data[0].url
        logging.info(f"이미지 생성 완료: {new_image_url}")

        # Step 2️⃣ DB 업데이트
        success = update_memory(
            memory_id,
            memory_update.text,
            memory_update.date,
            memory_update.gpt_analysis,
            new_image_url
        )

        if not success:
            raise HTTPException(status_code=404, detail="수정할 기억을 찾을 수 없습니다.")

        return {
            "status": "success",
            "message": f"기억(ID: {memory_id}) 수정 및 이미지 재생성 완료",
            "image_url": new_image_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"기억 수정 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 수정 중 오류 발생")


# memory 삭제 기능
@router.delete("/{memory_id}")
async def delete_memory_item(memory_id: int):
    """
    특정 기억 삭제
    """
    try:
        success = delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 기억을 찾을 수 없습니다.")
        return {"status": "success", "message": f"기억(ID: {memory_id}) 삭제 완료"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"기억 삭제 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 삭제 중 오류 발생")
