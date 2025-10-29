from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi import Request

from app.routers import memory, image

app = FastAPI(title="The Trace of Time Restored by AI")

# 라우터 등록
app.include_router(memory.router, prefix="/memory", tags=["Memory"])
app.include_router(image.router, prefix="/image", tags=["Image"])

# static 파일 경로 등록
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates 경로 등록
templates = Jinja2Templates(directory="templates")

# 루트 URL → index.html 렌더링
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Timeline 페이지
@app.get("/timeline", response_class=HTMLResponse)
async def timeline(request: Request):
    return templates.TemplateResponse("timeline.html", {"request": request})