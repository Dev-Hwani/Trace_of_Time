from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)

def generate_image(prompt: str) -> str:
    """텍스트 프롬프트 기반 이미지 생성 후 URL 반환"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        logging.error(f"이미지 생성 실패: {e}")
        return ""
