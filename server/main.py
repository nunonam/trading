"""FastAPI 서버 - Day Trading Backend"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from server.core.kis_client import kis
from server.services.scanner import scanner
from server.routers import stocks, portfolio, ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info("KIS 인증 시작")
    try:
        kis.authenticate(svr="prod", product="01")
        logger.info("KIS 인증 완료")
    except Exception as e:
        logger.error(f"KIS 인증 실패: {e} (API는 동작하지만 KIS 호출 불가)")

    # 5분 주기 급등주 스캔
    scheduler.add_job(scanner.scan, "interval", minutes=5, id="surge_scan")
    scheduler.start()
    logger.info("급등주 스캐너 시작 (5분 주기)")

    # 초기 스캔
    scanner.scan()

    yield

    # ── Shutdown ──
    scheduler.shutdown()
    logger.info("서버 종료")


app = FastAPI(title="Day Trading API", lifespan=lifespan)

# CORS (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(ws.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "kis_authenticated": kis.is_authenticated}
