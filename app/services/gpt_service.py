# gpt_service.py

from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)


def analyze_memory(text: str) -> dict:
    """GPT-4o를 이용하여 기억 텍스트를 분석하고 JSON 구조로 반환"""

    # 🔹 1. GPT에게 system_prompt 요청
    system_prompt = """
    당신은 감성 분석 전문가입니다.
    사용자가 제공한 기억 텍스트를 분석하여 아래 JSON 구조로 출력하세요.
    'Key'는 반드시 영어를 사용하고, 'Value'는 반드시 유창한 한국어로 작성합니다.
    출력 형식은 JSON으로만 제한하며, 절대 다른 텍스트를 포함하지 마세요.

    출력 JSON 구조:
    {
      "emotion": "",      # 기억에서 느껴지는 감정 (한글 값)
      "imagery": "",      # 기억을 시각적으로 표현할 수 있는 장면 (한글 값)
      "time_period": "",  # 기억이 연상되는 시대적 배경 (한글 값)
      "symbolism": ""     # 기억이 상징하는 의미나 주제 (한글 값)
    }
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        result_text = response.choices[0].message.content

        try:
            # 🔹 2. JSON 문자열 -> 파이썬 딕셔너리 (영어 키 + 한글 값)
            result_json = json.loads(result_text)

            # 🔹 3. index.js를 위한 'analysis' 키를 수동으로 생성
            # 4개의 한글 값을 하나의 요약 문자열로 합칩니다.
            analysis_summary = (
                f"감정: {result_json.get('emotion', '-')}\n"
                f"이미지: {result_json.get('imagery', '-')}\n"
                f"시대: {result_json.get('time_period', '-')}\n"
                f"상징: {result_json.get('symbolism', '-')}"
            )

            # 🔹 4. 'analysis' 키를 딕셔너리에 추가
            result_json["analysis"] = analysis_summary

        except json.JSONDecodeError:
            # GPT가 JSON 형식을 반환하지 않았을 경우
            result_json = {"analysis": result_text, "analysis_text": result_text}

        # 🔹 5. (최종 반환) 영어 키 4개 + analysis 키 1개가 포함된 딕셔너리
        return result_json

    except Exception as e:
        logging.error(f"GPT 분석 실패: {e}")
        return {"analysis_error": str(e), "analysis": "분석 중 오류가 발생했습니다."}