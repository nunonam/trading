"""KIS API client - kis/ 코드를 래핑하여 사용"""

import sys
import os
import logging
from datetime import datetime
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
    chk_holiday,
)
from domestic_stock_functions_ws import (
    ccnl_krx,
    asking_price_krx,
)


class KISClient:
    """KIS Open API 클라이언트"""

    def __init__(self):
        self._authenticated = False
        self._svr = "prod"

    def authenticate(self, svr: str = "prod", product: str = "01"):
        """인증 초기화"""
        self._svr = svr
        ka.auth(svr=svr, product=product)
        env = ka.getTREnv()
        if not isinstance(env, tuple) or not hasattr(env, "my_url"):
            raise RuntimeError("KIS 토큰 발급 실패 - kis_devlp.yaml의 앱키/시크릿을 확인하세요")
        self._authenticated = True

    def authenticate_ws(self, svr: str = "prod", product: str = "01"):
        """WebSocket 인증"""
        ka.auth_ws(svr=svr, product=product)

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    # ── 장 운영시간 체크 ──

    def check_market_open(self) -> bool:
        """당일 개장 여부 확인 (KIS 휴장일 API + 시간 체크)"""
        now = datetime.now()

        # 캐싱: 같은 날짜면 API 재호출 안 함
        today = now.strftime("%Y%m%d")
        if hasattr(self, "_market_open_cache") and self._market_open_cache[0] == today:
            is_open_day = self._market_open_cache[1]
        else:
            # 모의투자에서는 휴장일 API 미지원 (tr_id 자동 변환 문제)
            if self._svr == "vps":
                is_open_day = now.weekday() < 5
            else:
                try:
                    df = chk_holiday(bass_dt=today)
                    row = df[df["bass_dt"] == today]
                    is_open_day = not row.empty and row.iloc[0].get("opnd_yn") == "Y"
                except Exception as e:
                    logging.getLogger(__name__).warning(f"휴장일 조회 실패, 평일 기준 판단: {e}")
                    is_open_day = now.weekday() < 5
            self._market_open_cache = (today, is_open_day)

        if not is_open_day:
            return False

        # 장 운영시간: 09:00 ~ 15:30
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_open <= now <= market_close

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
            fid_cond_scr_div_code="20171",
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
        env = ka.getTREnv()
        result = inquire_balance(
            env_dv="demo" if self._svr == "vps" else "real",
            cano=env.my_acct,
            acnt_prdt_cd=env.my_prod,
            afhr_flpr_yn="N",
            inqr_dvsn="02",
            unpr_dvsn="01",
            fund_sttl_icld_yn="N",
            fncg_amt_auto_rdpt_yn="N",
            prcs_dvsn="01",
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
