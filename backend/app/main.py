# 파일 기능: FastAPI 애플리케이션 엔트리포인트로 라우터 등록, 미들웨어, 헬스체크, 시작 시 DB 초기화를 담당한다.
import sys
from pathlib import Path

# 현재 파일의 부모 디렉토리 (app)의 부모 디렉토리 (backend)의 부모 디렉토리 (Ajou-International)를 찾음
# 이 경로를 sys.path에 추가하여 프로젝트 root를 기준으로 모듈을 찾을 수 있도록 함
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import os
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .db_errors import db_connection_failed_response, log_db_exception, sanitize_db_error
from .database import SessionLocal
from .routers.auth import router as auth_router
from .routers.keywords import router as keywords_router
from .routers.notices import router as notices_router
from .routers.chatbot import router as chatbot_router
from .routers.information_menu import router as information_menu_router

logger = logging.getLogger("azan.main")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
app = FastAPI(title="azan-api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 로컬 개발 및 핫스팟 환경을 위해 일시적으로 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
# 입력: 없음
# 출력: None (DB 확장/인덱스 생성 및 시드 처리)
def on_startup() -> None:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Keep the app process alive so db-dependent endpoints can return controlled 500 errors.
        log_db_exception("Startup DB initialization failed", exc)
    except Exception as exc:
        logger.error("Startup initialization failed: %s", exc)
    finally:
        db.close()


@app.exception_handler(SQLAlchemyError)
# 입력: Request, SQLAlchemyError
# 출력: JSONResponse (DB 오류 응답)
def sqlalchemy_error_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
    return db_connection_failed_response(exc)


@app.get("/health")
# 입력: 없음
# 출력: dict[str, str] (서비스 상태)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", response_model=None)
# 입력: 없음
# 출력: dict 또는 JSONResponse (DB 상태)
def health_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except SQLAlchemyError as exc:
        message = sanitize_db_error(exc)
        log_db_exception("DB health check failed", exc)
        return JSONResponse(status_code=500, content={"db": "error", "message": message})
    finally:
        db.close()

app.include_router(auth_router)
app.include_router(keywords_router)
app.include_router(notices_router)
app.include_router(chatbot_router)
app.include_router(information_menu_router)


if __name__ == "__main__":
    # 환경변수 PORT가 없으면 8000 사용, 모든 인터페이스(0.0.0.0)에서 대기
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
