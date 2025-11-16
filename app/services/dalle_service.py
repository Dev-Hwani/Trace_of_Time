# app/services/dalle_service.py
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# 환경 변수 로드 및 클라이언트 생성
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)


def generate_image(prompt_or_gpt_result) -> str:
    """
    GPT 분석 결과(dict) 또는 텍스트(prompt)를 받아
    DALL-E-3 모델로 현실적이고 감성적인 이미지 생성 후 URL 반환.
    """
    # GPT 분석 결과일 경우 프롬프트 자동 생성
    if isinstance(prompt_or_gpt_result, dict):
        gpt_result = prompt_or_gpt_result
        prompt = (
            f"사용자의 기억을 사실적이고 감성적인 이미지로 재구성하세요.\n\n"
            f"감정: {gpt_result.get('emotion', '')}\n"
            f"감정 강도: {gpt_result.get('emotion_intensity', '')}\n"
            f"장면 묘사: {gpt_result.get('imagery', '')}\n"
            f"시각적 요소: {gpt_result.get('visual_elements', '')}\n"
            f"색조/조명: {gpt_result.get('color_tone', '')}\n"
            f"시간대/시대: {gpt_result.get('time_period', '')}\n"
            f"장소/환경: {gpt_result.get('location_context', '')}\n"
            f"상징적 의미: {gpt_result.get('symbolism', '')}\n"
            f"중점 피사체: {gpt_result.get('visual_focus', '')}\n"
            f"카메라 시점: {gpt_result.get('camera_perspective', '')}\n\n"
            f"사진처럼 현실적이고 세부적인 묘사, 감정과 시간 흐름이 느껴지도록 구성하세요."
        )
    else:
        # 문자열 프롬프트 그대로 사용
        prompt = str(prompt_or_gpt_result)

    try:
        # 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024"
        )

        image_url = response.data[0].url
        logging.info(f"이미지 생성 성공: {image_url}")
        return image_url

    except Exception as e:
        logging.error(f"이미지 생성 실패: {e}", exc_info=True)
        return ""
