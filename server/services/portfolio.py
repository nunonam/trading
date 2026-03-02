"""포트폴리오 관리 - 잔고 조회 및 수익률 계산"""

import logging

from server.core.kis_client import kis

logger = logging.getLogger(__name__)


class PortfolioManager:
    """포트폴리오 관리"""

    def get_balance(self) -> dict:
        """잔고 조회"""
        try:
            if not kis.is_authenticated:
                return {"holdings": [], "summary": {}, "daily_profit_rate": 0}

            data = kis.get_balance()
            holdings = []
            for h in data.get("holdings", []):
                holdings.append({
                    "code": h.get("pdno", ""),
                    "name": h.get("prdt_name", ""),
                    "quantity": int(h.get("hldg_qty", 0)),
                    "avg_price": float(h.get("pchs_avg_pric", 0)),
                    "current_price": int(h.get("prpr", 0)),
                    "profit_rate": float(h.get("evlu_pfls_rt", 0)),
                    "profit_amount": int(h.get("evlu_pfls_amt", 0)),
                    "eval_amount": int(h.get("evlu_amt", 0)),
                })

            summary_list = data.get("summary", [])
            summary = summary_list[0] if summary_list else {}

            total_eval = int(summary.get("tot_evlu_amt", 0))
            total_purchase = int(summary.get("pchs_amt_smtl_amt", 0))
            daily_profit = total_eval - total_purchase
            daily_profit_rate = (daily_profit / total_purchase * 100) if total_purchase > 0 else 0

            return {
                "holdings": holdings,
                "summary": {
                    "total_eval": total_eval,
                    "total_purchase": total_purchase,
                    "daily_profit_amount": daily_profit,
                    "daily_profit_rate": round(daily_profit_rate, 2),
                    "cash_balance": int(summary.get("dnca_tot_amt", 0)),
                },
            }

        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
            return {"holdings": [], "summary": {}, "error": str(e)}


portfolio = PortfolioManager()
