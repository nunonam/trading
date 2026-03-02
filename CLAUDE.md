# Day Trading Web App

## Project Overview

KIS Open API를 활용한 국내주식 데이트레이딩 웹 애플리케이션.
일간 최소 2% 이상 수익률 달성을 목표로 한 자동 모니터링 + 반자동 매매 시스템.

## Tech Stack

- **Frontend**: Vite + React + TypeScript
- **Backend**: FastAPI (Python)
- **KIS API**: `kis/` 디렉토리의 Python 코드를 server에서 import
- **Real-time**: WebSocket (FastAPI → React)
- **Scheduler**: APScheduler (5분 주기 스캔)

## Project Structure

```
.
├── CLAUDE.md
├── .gitignore
├── kis/                          # KIS Open API 코드 (Python)
│   ├── for_llm/                  # LLM용 API 단위 샘플
│   ├── for_user/                 # 사용자용 통합 예제
│   │   ├── kis_auth.py           # 인증 모듈
│   │   └── domestic_stock/       # 국내주식 함수 (REST + WebSocket)
│   ├── stocks_info/              # 종목 마스터 정보
│   └── kis_devlp.yaml            # API 인증 설정
├── server/                       # FastAPI 백엔드
│   ├── main.py                   # 앱 엔트리 (lifespan, 스케줄러)
│   ├── core/
│   │   └── kis_client.py         # KIS API 래퍼 (싱글톤)
│   ├── services/
│   │   ├── scanner.py            # 급등주 5분 주기 스캐너
│   │   └── portfolio.py          # 잔고/수익률 관리
│   ├── routers/
│   │   ├── stocks.py             # GET /api/stocks/*
│   │   ├── portfolio.py          # GET/POST /api/portfolio/*
│   │   └── ws.py                 # WS /ws/prices
│   └── requirements.txt
├── src/                          # React 프론트엔드 (Vite)
│   ├── components/
│   ├── types/
│   └── data/
├── vite.config.ts                # Vite 설정 (proxy → :8000)
└── package.json
```

## How to Run

```bash
# 1. Backend
pip install -r server/requirements.txt
uvicorn server.main:app --reload

# 2. Frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | 서버 상태 & KIS 인증 여부 |
| GET | `/api/stocks/watchlist` | 급등주 스캔 결과 (5분 자동갱신) |
| GET | `/api/stocks/price/{code}` | 종목 현재가 |
| GET | `/api/stocks/chart/{code}` | 분봉 차트 데이터 |
| POST | `/api/stocks/scan` | 수동 급등주 스캔 |
| GET | `/api/portfolio/balance` | 잔고 조회 |
| POST | `/api/portfolio/buy` | 매수 주문 |
| POST | `/api/portfolio/sell` | 매도 주문 |
| WS | `/ws/prices` | 실시간 시세 구독 |

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│ Header: 현재 수익률 표시                               │
├───────────────────────────────────┬─────────────────┤
│ Main Left (80%)                   │ Main Right (20%)│
│                                   │                 │
│ 관심종목 카드들                      │ 매수종목 카드들   │
│ - 급등주 모니터링 결과               │ - 보유 종목      │
│ - VWAP/EMA 시그널 표시              │ - 수익률 표시    │
│ - 매수 버튼                        │ - 매도 버튼      │
│                                   │ - 손절 상태      │
│                                   │                 │
└───────────────────────────────────┴─────────────────┘
```

## Day Trading Strategy

### 목표

- 일간 수익률: **최소 +2%**
- 최대 손실 허용: **-2%**

### Phase 1: 급등주 모니터링 (장 시작 ~ 관심종목 선정)

- 장 시작 후 **5분 주기**로 급등주 스캔
- 스캔 기준:
  - 전일 대비 등락률 상위
  - 거래량 급증 종목
  - 시가 대비 상승률
- 조건 충족 시 **관심종목 카드**에 자동 추가

### Phase 2: 관심종목 실시간 모니터링 (WebSocket + 5분봉)

- 관심종목을 **WebSocket으로 실시간 구독**
- **5분봉** 기반 기술적 분석
- **매수 시그널 판단**:
  - **VWAP (Volume Weighted Average Price)**: 현재가가 VWAP 위에서 지지받는지 확인
  - **EMA (Exponential Moving Average)**: 단기 EMA(9) > 중기 EMA(20) 골든크로스
  - VWAP 위 + EMA 골든크로스 동시 충족 시 매수 시그널 발생

### Phase 3: 분할 매수

- 매수 단위: **전체 투자금의 10%** 씩 분할 매수
- 매수 조건:
  - VWAP + EMA 전략 시그널 충족
  - 5분봉 캔들 확인 후 진입
- 최대 매수 비중: 종목당 제한 설정 필요

### Phase 4: 분할 매도 (익절)

- **+2% 수익 달성 시** 10%씩 분할 매도 시작
- **Swing High Break 모니터링**:
  - 5분봉 기준 직전 고점(Swing High) 돌파 여부 확인
  - 고점 돌파 실패 시 추가 매도
  - 고점 갱신 시 홀딩 유지, 새로운 Swing High 기준 재설정

### Phase 5: 손절 (분할 손절)

- **-1% 도달 시** 10%씩 분할 손절 시작
- **-2% 최대 손절선**: 남은 물량 전량 매도
- **Swing Low Break 모니터링**:
  - 5분봉 기준 직전 저점(Swing Low) 이탈 여부 확인
  - 저점 이탈 시 즉시 추가 손절
  - 저점 지지 시 홀딩 유지, 반등 여부 관찰

### Key Indicators Summary

| 지표 | 용도 | 설정 |
|------|------|------|
| VWAP | 매수 기준선 | 당일 누적 거래량 가중 평균가 |
| EMA(9) | 단기 추세 | 9봉 지수이동평균 |
| EMA(20) | 중기 추세 | 20봉 지수이동평균 |
| Swing High | 익절 기준 | 5분봉 직전 고점 |
| Swing Low | 손절 기준 | 5분봉 직전 저점 |

### Risk Management Rules

- 종목당 최대 투자 비중 제한
- 일간 최대 손실 -2% 도달 시 당일 매매 중단
- 분할 매수/매도로 평균 단가 리스크 분산
- 장 종료 30분 전 미체결 포지션 정리 검토
