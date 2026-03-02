"""급등주 스캐너 - 5분 주기 모니터링"""

import logging
from datetime import datetime

from server.core.kis_client import kis

logger = logging.getLogger(__name__)


class SurgeScanner:
    """급등주 스캐너: 5분마다 실행"""

    def __init__(self):
        self.watchlist: list[dict] = []
        self.last_scan: datetime | None = None

    def scan(self):
        """급등주 스캔 실행"""
        try:
            if not kis.is_authenticated:
                logger.warning("KIS 미인증 상태 - 스캔 스킵")
                return

            logger.info("급등주 스캔 시작")
            results = kis.scan_volume_surge()

            candidates = []
            for stock in results:
                # 거래량 급증 + 상승 종목 필터
                change_rate = float(stock.get("prdy_ctrt", 0))
                if change_rate > 1.0:
                    candidates.append({
                        "code": stock.get("mksc_shrn_iscd", ""),
                        "name": stock.get("hts_kor_isnm", ""),
                        "current_price": int(stock.get("stck_prpr", 0)),
                        "change_rate": change_rate,
                        "volume": int(stock.get("acml_vol", 0)),
                        "volume_rate": float(stock.get("vol_inrt", 0)),
                        "scanned_at": datetime.now().strftime("%H:%M"),
                    })

            self.watchlist = candidates[:20]
            self.last_scan = datetime.now()
            logger.info(f"급등주 스캔 완료: {len(self.watchlist)}종목")

        except Exception as e:
            logger.error(f"급등주 스캔 실패: {e}")

    def get_watchlist(self) -> dict:
        return {
            "stocks": self.watchlist,
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "count": len(self.watchlist),
        }


scanner = SurgeScanner()
