"""WebSocket 엔드포인트 - 실시간 시세 중계"""

import json
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.core.kis_client import kis

router = APIRouter()
logger = logging.getLogger(__name__)

# 연결된 클라이언트 관리
_clients: set[WebSocket] = set()


async def broadcast(data: dict):
    """모든 클라이언트에 메시지 브로드캐스트"""
    dead = set()
    for ws in _clients:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    _clients -= dead


@router.websocket("/ws/prices")
async def ws_prices(websocket: WebSocket):
    """실시간 시세 WebSocket

    클라이언트가 subscribe/unsubscribe 메시지를 보내면
    해당 종목의 시세를 주기적으로 전송.

    메시지 형식:
      {"action": "subscribe", "codes": ["005930", "000660"]}
      {"action": "unsubscribe", "codes": ["005930"]}
    """
    await websocket.accept()
    _clients.add(websocket)

    subscribed_codes: set[str] = set()
    poll_task: asyncio.Task | None = None

    async def poll_prices():
        """구독 종목의 시세를 5초마다 폴링"""
        while True:
            try:
                for code in list(subscribed_codes):
                    price = kis.get_price(code)
                    if price:
                        await websocket.send_json({
                            "type": "price",
                            "code": code,
                            "data": price,
                        })
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"시세 폴링 오류: {e}")
                await asyncio.sleep(5)

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")

            if action == "subscribe":
                codes = msg.get("codes", [])
                subscribed_codes.update(codes)
                logger.info(f"구독 추가: {codes}, 전체: {subscribed_codes}")

                # 폴링 시작
                if poll_task is None or poll_task.done():
                    poll_task = asyncio.create_task(poll_prices())

            elif action == "unsubscribe":
                codes = msg.get("codes", [])
                subscribed_codes -= set(codes)
                logger.info(f"구독 해제: {codes}, 남은: {subscribed_codes}")

                if not subscribed_codes and poll_task:
                    poll_task.cancel()
                    poll_task = None

    except WebSocketDisconnect:
        logger.info("WebSocket 연결 종료")
    finally:
        _clients.discard(websocket)
        if poll_task:
            poll_task.cancel()
