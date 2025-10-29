# Trace_of_Time

## 프로젝트 구조
The_Trace_of_Time_Restored_by_AI/
├── .venv/                     # Python 가상환경
├── app/                       # FastAPI 애플리케이션 코드
│   ├── models/
│   │   └── memory_model.py    # DB에 memory 데이터 저장/조회 관련 로직
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── image.py            # image 생성 관련 API 라우터 (/image)
│   │   └── memory.py           # memory 관련 API 라우터 (/memory)
│   ├── schemas/
│   │   └── memory_schema.py    # Pydantic 모델 정의 (API 요청 데이터 검증)
│   ├── services/
│   │   ├── gpt_service.py      # GPT를 이용한 memory 분석
│   │   └── dalle_service.py    # DALL-E-3를 이용한 이미지 생성
│   ├── utils/
│   │   └── __init__.py         # 필요 시 유틸리티 함수 추가
│   └── __init__.py
├── database/
│   └── connection.py           # MySQL DB 연결
├── static/
│   ├── images/
│   ├── css/
│   │   └── style.css           # 웹 페이지 스타일
│   └── js/
│       ├── index.js            # Memory 입력 페이지 JS (API 호출, UI 동작)
│       └── timeline.js         # Timeline 조회 페이지 JS (모달, 카드 렌더링)
├── templates/
│   ├── base.html               # 공통 레이아웃, 네비게이션바 포함
│   ├── index.html              # Memory 입력 페이지
│   └── timeline.html           # Timeline 조회 페이지
├── .env                        # 환경 변수 파일 (DB 정보, OpenAI API 키)
├── main.py                     # FastAPI 앱 실행 및 라우터 등록
├── test_main.http              # API 테스트용 HTTP 요청 예시
└── requirements.txt            # 프로젝트 의존성 패키지 목록

## 설치 및 실행 방법
### 1. 프로젝트 다운로드

### 2. 가상환경 삭제 후 재설치
python -m venv .venv
.\.venv\Scripts\activate

### 3. 필요 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

### 4. 환경 변수 설정
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=memory_db

### 5. MySQL DB 준비
CREATE DATABASE memory_db;

USE memory_db;

CREATE TABLE memory_archive (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text LONGTEXT NOT NULL,
    date DATE,
    gpt_analysis JSON,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

### 6. FastAPI 서버 실행
uvicorn main:app --reload
기본 URL: http://127.0.0.1:8000
API 문서: http://127.0.0.1:8000/docs
