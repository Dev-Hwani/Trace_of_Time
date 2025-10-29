from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logging.basicConfig(level=logging.INFO)

def analyze_memory(text: str) -> dict:
    """GPT-4를 이용하여 기억 텍스트를 감성적으로 분석하고 JSON 구조로 반환"""
    system_prompt = """
    당신은 감성 분석 전문가입니다.
    사용자가 제공한 기억 텍스트를 분석하여 아래 JSON 구조로 출력하세요:
    {
      "emotion": "",
      "imagery": "",
      "time_period": "",
      "symbolism": ""
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
        # GPT가 JSON 형식으로 반환했다고 가정하고 dict로 변환
        import json
        try:
            result_json = json.loads(result_text)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            result_json = {"analysis_text": result_text}

        return result_json
    except Exception as e:
        logging.error(f"GPT 분석 실패: {e}")
        return {"analysis_error": str(e)}
