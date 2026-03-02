"""주식 시세 & 관심종목 API"""

from fastapi import APIRouter

from server.core.kis_client import kis
from server.services.scanner import scanner

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/watchlist")
async def get_watchlist():
    """관심종목 (급등주 스캔 결과)"""
    return scanner.get_watchlist()


@router.get("/price/{code}")
async def get_price(code: str):
    """종목 현재가"""
    return kis.get_price(code)


@router.get("/chart/{code}")
async def get_chart(code: str):
    """분봉 차트 데이터"""
    return kis.get_chart_minutes(code)


@router.post("/scan")
async def trigger_scan():
    """수동 급등주 스캔"""
    scanner.scan()
    return scanner.get_watchlist()
