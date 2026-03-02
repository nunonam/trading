"""FastAPI 서버 - DISTONE TRADING Backend"""

import os
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
    svr = os.environ.get("KIS_MODE", "prod")
    logger.info(f"KIS 인증 시작 (mode={svr})")
    try:
        kis.authenticate(svr=svr, product="01")
        logger.info("KIS 인증 완료")
    except Exception as e:
        logger.error(f"KIS 인증 실패: {e}")

    if kis.is_authenticated:
        # 5분 주기 급등주 스캔
        scheduler.add_job(scanner.scan, "interval", minutes=5, id="surge_scan")
        scheduler.start()
        logger.info("급등주 스캐너 시작 (5분 주기)")
        scanner.scan()
    else:
        logger.warning("KIS 미인증 - 스캐너 비활성화 (서버는 동작)")

    yield

    # ── Shutdown ──
    scheduler.shutdown()
    logger.info("서버 종료")


app = FastAPI(title="DISTONE TRADING API", lifespan=lifespan)

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
    return {
        "status": "ok",
        "kis_authenticated": kis.is_authenticated,
        "market_open": kis.check_market_open() if kis.is_authenticated else False,
    }
