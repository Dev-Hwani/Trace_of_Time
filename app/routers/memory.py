import logging
from fastapi import APIRouter, HTTPException

from app.models.memory_model import delete_memory, get_all_memories, save_memory, update_memory
from app.schemas.memory_schema import MemoryInput, MemoryUpdate
from app.services.dalle_service import generate_image
from app.services.gpt_service import analyze_memory

router = APIRouter()
logging.basicConfig(level=logging.INFO)


@router.post("/create")
async def create_memory(memory: MemoryInput):
    """기억 생성: GPT 분석, 이미지 생성, DB 저장"""
    try:
        logging.info("Memory 생성 요청: text='{}...' date='{}'".format(memory.text[:30], memory.date))

        # GPT 분석
        try:
            gpt_result = analyze_memory(memory.text)
            logging.info(f"GPT 분석 결과: {gpt_result}")
        except Exception as gpt_err:
            logging.error(f"GPT 분석 실패: {gpt_err}")
            raise HTTPException(status_code=502, detail="GPT 분석 실패")

        # 이미지 생성
        try:
            image_val = gpt_result.get("이미지", memory.text)
            emotion_val = gpt_result.get("감정", "")
            era_val = gpt_result.get("시대", "")
            combined_prompt = f"{image_val} {emotion_val} {era_val}".strip() or memory.text
            image_url = generate_image(combined_prompt)
            if not image_url:
                raise ValueError("이미지 URL 생성 실패")
            logging.info(f"이미지 생성 결과: {image_url}")
        except Exception as img_err:
            logging.error(f"이미지 생성 실패: {img_err}")
            raise HTTPException(status_code=502, detail="이미지 생성 실패")

        # DB 저장
        memory_id = save_memory(memory.text, memory.date, gpt_result, image_url)
        if memory_id is None:
            logging.error("Memory DB 저장 실패")
            raise HTTPException(status_code=500, detail="DB 저장 실패")

        return {
            "status": "success",
            "memory_id": memory_id,
            "memory_text": memory.text,
            "gpt_analysis": gpt_result,
            "image_url": image_url,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Memory 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 생성 처리 중 오류 발생")


@router.get("/all")
async def get_memories():
    """모든 기억을 날짜순으로 조회"""
    try:
        memories = get_all_memories()
        logging.info(f"{len(memories)}개의 기억 조회 완료")
        return memories
    except Exception as e:
        logging.error(f"기억 조회 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 조회 처리 중 오류 발생")


@router.put("/{memory_id}")
async def update_memory_item(memory_id: int, memory_update: MemoryUpdate):
    """지정된 기억 수정 (텍스트, 분석, 이미지 재생성)"""
    try:
        prompt = f"{memory_update.date}의 기억: {memory_update.text}"
        logging.info(f"이미지 생성 시도 (프롬프트: {prompt})")

        # 권한 문제 없는 dall-e-3 기반 helper 사용
        new_image_url = generate_image(prompt)
        if not new_image_url:
            raise HTTPException(status_code=502, detail="이미지 생성 실패")

        success = update_memory(
            memory_id,
            memory_update.text,
            memory_update.date,
            memory_update.gpt_analysis,
            new_image_url,
        )

        if not success:
            raise HTTPException(status_code=404, detail="수정할 기억을 찾을 수 없습니다.")

        return {
            "status": "success",
            "message": f"기억(ID: {memory_id}) 수정 및 이미지 생성 완료",
            "image_url": new_image_url,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"기억 수정 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 수정 처리 중 오류 발생")


@router.delete("/{memory_id}")
async def delete_memory_item(memory_id: int):
    """지정된 기억 삭제"""
    try:
        success = delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 기억을 찾을 수 없습니다.")
        return {"status": "success", "message": f"기억(ID: {memory_id}) 삭제 완료"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"기억 삭제 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="기억 삭제 처리 중 오류 발생")
