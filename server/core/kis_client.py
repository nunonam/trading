"""KIS API client - kis/ 코드를 래핑하여 사용"""

import sys
import os
from pathlib import Path

# kis/ 모듈 경로 추가
_kis_root = Path(__file__).resolve().parent.parent.parent / "kis"
_kis_user = _kis_root / "for_user"
_kis_stock = _kis_user / "domestic_stock"

for p in [str(_kis_user), str(_kis_stock)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import kis_auth as ka
from domestic_stock_functions import (
    inquire_price,
    inquire_daily_price,
    inquire_time_itemchartprice,
    inquire_balance,
    order_cash,
    after_hour_balance,
    volume_rank,
)
from domestic_stock_functions_ws import (
    ccnl_krx,
    asking_price_krx,
)


class KISClient:
    """KIS Open API 클라이언트"""

    def __init__(self):
        self._authenticated = False

    def authenticate(self, svr: str = "prod", product: str = "01"):
        """인증 초기화"""
        ka.auth(svr=svr, product=product)
        self._authenticated = True

    def authenticate_ws(self, svr: str = "prod", product: str = "01"):
        """WebSocket 인증"""
        ka.auth_ws(svr=svr, product=product)

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    # ── 시세 조회 ──

    def get_price(self, code: str, market: str = "J") -> dict:
        """현재가 조회"""
        df = inquire_price(fid_cond_mrkt_div_code=market, fid_input_iscd=code)
        if df is not None and not df.empty:
            return df.to_dict("records")[0]
        return {}

    def get_daily_prices(self, code: str, period: str = "D", market: str = "J") -> list[dict]:
        """일별 시세"""
        df = inquire_daily_price(
            fid_cond_mrkt_div_code=market,
            fid_input_iscd=code,
            fid_period_div_code=period,
        )
        if df is not None and not df.empty:
            return df.to_dict("records")
        return []

    def get_chart_minutes(self, code: str, market: str = "J") -> list[dict]:
        """분봉 차트 (5분봉용)"""
        df = inquire_time_itemchartprice(
            fid_cond_mrkt_div_code=market,
            fid_input_iscd=code,
            fid_etc_cls_code="",
            fid_input_hour_1="",
        )
        if df is not None and not df.empty:
            return df.to_dict("records")
        return []

    # ── 급등주 스캔 ──

    def scan_volume_surge(self) -> list[dict]:
        """거래량 급증 종목 스캔"""
        df = volume_rank(
            fid_cond_mrkt_div_code="J",
            fid_cond_scr_div_code="20101",
            fid_input_iscd="0000",
            fid_div_cls_code="0",
            fid_blng_cls_code="0",
            fid_trgt_cls_code="111111111",
            fid_trgt_exls_cls_code="0000000000",
            fid_input_price_1="",
            fid_input_price_2="",
            fid_vol_cnt="",
            fid_input_date_1="",
        )
        if df is not None and not df.empty:
            return df.head(20).to_dict("records")
        return []

    def scan_after_hour_surge(self) -> list[dict]:
        """시간외 잔량 급등 종목"""
        df = after_hour_balance(
            fid_input_price_1="",
            fid_cond_mrkt_div_code="J",
            fid_rank_sort_cls_code="0",
            fid_input_iscd="0000",
            fid_cond_scr_div_code="20176",
            fid_div_cls_code="0",
            fid_blng_cls_code="3",
            fid_trgt_cls_code="0",
            fid_trgt_exls_cls_code="0",
            fid_input_price_2="",
        )
        if df is not None and not df.empty:
            return df.head(20).to_dict("records")
        return []

    # ── 잔고 ──

    def get_balance(self) -> dict:
        """잔고 조회 (보유종목 + 예수금)"""
        result = inquire_balance(
            afhr_flpr_yn="N",
            ofl_yn="",
            inqr_dvsn="02",
            unpr_dvsn="01",
            fund_sttl_icld_yn="N",
            fncg_amt_auto_rdpt_yn="N",
            prcs_dvsn="01",
            cost_icld_yn="Y",
        )
        if result and isinstance(result, tuple) and len(result) == 2:
            holdings_df, summary_df = result
            return {
                "holdings": holdings_df.to_dict("records") if holdings_df is not None and not holdings_df.empty else [],
                "summary": summary_df.to_dict("records") if summary_df is not None and not summary_df.empty else [],
            }
        return {"holdings": [], "summary": []}

    # ── 주문 ──

    def buy(self, code: str, qty: int, price: int = 0, order_type: str = "00") -> dict:
        """매수 주문 (order_type: 00=지정가, 01=시장가)"""
        result = order_cash(
            ord_dv="buy",
            ord_unpr=str(price),
            ord_qty=str(qty),
            pdno=code,
            ord_dvsn=order_type,
        )
        if result is not None:
            if hasattr(result, "to_dict"):
                return result.to_dict("records")[0] if not result.empty else {}
            return result if isinstance(result, dict) else {}
        return {}

    def sell(self, code: str, qty: int, price: int = 0, order_type: str = "00") -> dict:
        """매도 주문"""
        result = order_cash(
            ord_dv="sell",
            ord_unpr=str(price),
            ord_qty=str(qty),
            pdno=code,
            ord_dvsn=order_type,
        )
        if result is not None:
            if hasattr(result, "to_dict"):
                return result.to_dict("records")[0] if not result.empty else {}
            return result if isinstance(result, dict) else {}
        return {}

    # ── WebSocket 헬퍼 ──

    def ws_subscribe_ccnl(self, code: str) -> tuple[dict, list[str]]:
        """체결 실시간 구독 메시지 생성"""
        return ccnl_krx(tr_type="1", tr_key=code)

    def ws_subscribe_asking(self, code: str) -> tuple[dict, list[str]]:
        """호가 실시간 구독 메시지 생성"""
        return asking_price_krx(tr_type="1", tr_key=code)


# 싱글톤
kis = KISClient()
