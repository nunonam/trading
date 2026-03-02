"""포트폴리오 & 주문 API"""

from fastapi import APIRouter
from pydantic import BaseModel

from server.core.kis_client import kis
from server.services.portfolio import portfolio as portfolio_mgr

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


class OrderRequest(BaseModel):
    code: str
    quantity: int
    price: int = 0
    order_type: str = "00"  # 00=지정가, 01=시장가


@router.get("/balance")
async def get_balance():
    """잔고 조회"""
    return portfolio_mgr.get_balance()


@router.post("/buy")
async def buy(req: OrderRequest):
    """매수 주문"""
    result = kis.buy(req.code, req.quantity, req.price, req.order_type)
    return {"ok": True, "data": result}


@router.post("/sell")
async def sell(req: OrderRequest):
    """매도 주문"""
    result = kis.sell(req.code, req.quantity, req.price, req.order_type)
    return {"ok": True, "data": result}
