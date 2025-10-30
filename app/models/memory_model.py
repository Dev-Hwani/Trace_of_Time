from database.connection import get_connection
import json
import logging

logging.basicConfig(level=logging.INFO)

def save_memory(text, date, gpt_analysis, image_url):
    """기억과 분석, 이미지 URL을 DB에 저장"""
    conn = get_connection()
    if conn is None:
        logging.error("DB 연결 실패: save_memory 수행 불가")
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO memory_archive (text, date, gpt_analysis, image_url) VALUES (%s, %s, %s, %s)"
        gpt_analysis_json = json.dumps(gpt_analysis, ensure_ascii=False)
        cursor.execute(sql, (text, date, gpt_analysis_json, image_url))
        conn.commit()
        inserted_id = cursor.lastrowid
        logging.info(f"Memory 저장 성공 (ID: {inserted_id})")
        return inserted_id
    except json.JSONDecodeError as je:
        logging.error(f"gpt_analysis JSON 직렬화 실패: {je}")
        return None
    except Exception as e:
        logging.error(f"DB 저장 실패: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_memories():
    """모든 기억 조회 (날짜 기준 오름차순)"""
    conn = get_connection()
    if conn is None:
        logging.error("DB 연결 실패: get_all_memories 수행 불가")
        return []

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id, text, date, gpt_analysis, image_url FROM memory_archive ORDER BY date ASC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            try:
                row['gpt_analysis'] = json.loads(row['gpt_analysis'])
            except json.JSONDecodeError as je:
                logging.warning(f"gpt_analysis JSON 파싱 실패 (ID: {row['id']}): {je}")
                row['gpt_analysis'] = {}
        logging.info(f"{len(rows)}개의 메모리 조회 완료")
        return rows
    except Exception as e:
        logging.error(f"DB 조회 실패: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()