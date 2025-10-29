from database.connection import get_connection
import json
import logging

logging.basicConfig(level=logging.INFO)

def save_memory(text, date, gpt_analysis, image_url):
    """기억과 분석, 이미지 URL을 DB에 저장"""
    conn = get_connection()
    if conn is None:
        logging.error("DB 연결 실패로 저장 불가")
        return None

    try:
        cursor = conn.cursor()
        sql = "INSERT INTO memory_archive (text, date, gpt_analysis, image_url) VALUES (%s, %s, %s, %s)"
        # gpt_analysis는 dict 형태로 들어오므로 내부에서 JSON 직렬화
        gpt_analysis_json = json.dumps(gpt_analysis, ensure_ascii=False)
        cursor.execute(sql, (text, date, gpt_analysis_json, image_url))
        conn.commit()
        inserted_id = cursor.lastrowid
        logging.info(f"Memory 저장 완료 (ID: {inserted_id})")
        return inserted_id
    except Exception as e:
        logging.error(f"DB 저장 실패: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT id, text, date, gpt_analysis, image_url FROM memory_archive ORDER BY date ASC"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        # gpt_analysis를 dict로 변환
        row['gpt_analysis'] = json.loads(row['gpt_analysis'])
    cursor.close()
    conn.close()
    return rows