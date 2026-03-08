import { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import WatchCard from './components/WatchCard';
import HoldingCard from './components/HoldingCard';
import Toast from './components/Toast';
import type { WatchStock, HoldingStock, PortfolioSummary } from './types/stock';
import './App.css';

const POLL_INTERVAL = 60 * 1000; // 1분

export default function App() {
  const [portfolio, setPortfolio] = useState<PortfolioSummary>({
    totalInvested: 0,
    totalValue: 0,
    dailyProfitRate: 0,
    dailyProfitAmount: 0,
    cashBalance: 0,
  });
  const [watchList, setWatchList] = useState<WatchStock[]>([]);
  const [holdings, setHoldings] = useState<HoldingStock[]>([]);
  const [marketOpen, setMarketOpen] = useState<boolean | null>(null);
  const [mode, setMode] = useState<'prod' | 'vps'>('prod');
  const [scanning, setScanning] = useState(false);
  const [toasts, setToasts] = useState<{ id: number; message: string }[]>([]);
  const toastId = useRef(0);

  const addToast = useCallback((message: string) => {
    const id = ++toastId.current;
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3000);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const fetchHealth = useCallback(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        setMarketOpen(data.market_open ?? false);
        setMode(data.mode ?? 'prod');
      })
      .catch(() => {
        setMarketOpen(false);
        addToast('서버 연결 실패');
      });
  }, [addToast]);

  const fetchWatchlist = useCallback(() => {
    setScanning(true);
    fetch('/api/stocks/watchlist')
      .then((res) => res.json())
      .then((data) => {
        const stocks: WatchStock[] = (data.stocks ?? []).map(
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (s: any) => ({
            code: s.code,
            name: s.name,
            currentPrice: s.current_price,
            changeRate: s.change_rate,
            volume: s.volume,
            volumeRate: s.volume_rate,
            scannedAt: s.scanned_at,
          }),
        );
        setWatchList(stocks);
      })
      .catch(() => addToast('관심종목 조회 실패'))
      .finally(() => setScanning(false));
  }, [addToast]);

  const fetchBalance = useCallback(() => {
    fetch('/api/portfolio/balance')
      .then((res) => res.json())
      .then((data) => {
        const summary = data.summary ?? {};
        setPortfolio({
          totalInvested: summary.total_purchase ?? 0,
          totalValue: summary.total_eval ?? 0,
          dailyProfitRate: summary.daily_profit_rate ?? 0,
          dailyProfitAmount: summary.daily_profit_amount ?? 0,
          cashBalance: summary.cash_balance ?? 0,
        });
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const h: HoldingStock[] = (data.holdings ?? []).map((s: any) => ({
          code: s.code,
          name: s.name,
          avgPrice: s.avg_price,
          currentPrice: s.current_price,
          quantity: s.quantity,
          profitRate: s.profit_rate,
          profitAmount: s.profit_amount,
          evalAmount: s.eval_amount,
        }));
        setHoldings(h);
      })
      .catch(() => addToast('잔고 조회 실패'));
  }, [addToast]);

  // 초기 로드
  useEffect(() => {
    fetchHealth();
    fetchWatchlist();
    fetchBalance();
  }, [fetchHealth, fetchWatchlist, fetchBalance]);

  // 5분 주기 폴링
  useEffect(() => {
    const id = setInterval(() => {
      fetchHealth();
      fetchWatchlist();
      fetchBalance();
    }, POLL_INTERVAL);
    return () => clearInterval(id);
  }, [fetchHealth, fetchWatchlist, fetchBalance]);

  return (
    <div className="app">
      <Header portfolio={portfolio} marketOpen={marketOpen} mode={mode} />
      <main className="main">
        <section className="panel panel-watch">
          <h2 className="panel-title">
            관심종목 ({watchList.length})
            {scanning && <span className="scan-badge">스캔중</span>}
          </h2>
          <div className="card-list">
            {watchList.map((stock) => (
              <WatchCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
        <section className="panel panel-holdings">
          <h2 className="panel-title">매수종목 ({holdings.length})</h2>
          <div className="card-list">
            {holdings.map((stock) => (
              <HoldingCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
      </main>
      <Toast toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
