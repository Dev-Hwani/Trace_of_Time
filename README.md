# Trace_of_Time

## 프로젝트 소개
The Trace of Time 프로젝트는 사용자의 기억을 입력받아 AI(GPT-4o)로 감정 분석을 수행하고
분석 결과와 관련 이미지를 생성하여 개인 타임라인에 시각화하는 웹 애플리케이션입니다.

## 주요 기능
- 기억 입력: 사용자가 경험한 기억을 텍스트로 입력
- AI 분석: GPT를 이용하여 감정, 이미지, 상징, 시대 분석
- AI 이미지 생성: DALL-E 3를 이용한 기억 이미지 생성
- 타임라인 조회: 저장된 기억과 AI 분석 결과를 카드 형태로 시각화
- 상세 모달: 카드 클릭 시 전체 텍스트와 분석 결과 확인
- 복원 재시도 기능 : 같은 기억이라도 다른 감정으로 재해석해볼 수 있도록 다시 복원 기능 제공

## 기술 스택
- Backend: Python, FastAPI
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Database: MySQL
- AI: OpenAI GPT-4o, DALL-E-3

## 프로젝트 구조
```
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
```

## 설치 및 실행 방법
### 1. 프로젝트 다운로드
```
<> Code -→ Download ZIP
```

### 2. 가상환경 삭제 후 재설치
```
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. 필요 패키지 설치
```
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=memory_db
```

### 5. MySQL DB 준비
```
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
```

### 6. FastAPI 서버 실행
```
uvicorn main:app --reload
```
기본 URL: http://127.0.0.1:8000

API 문서: http://127.0.0.1:8000/docs
