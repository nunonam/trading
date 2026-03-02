import { useState, useEffect } from 'react';
import Header from './components/Header';
import WatchCard from './components/WatchCard';
import HoldingCard from './components/HoldingCard';
import type { WatchStock, HoldingStock, PortfolioSummary } from './types/stock';
import './App.css';

export default function App() {
  const [portfolio] = useState<PortfolioSummary>({
    totalInvested: 0,
    totalValue: 0,
    dailyProfitRate: 0,
    dailyProfitAmount: 0,
    cashBalance: 0,
  });
  const [watchList] = useState<WatchStock[]>([]);
  const [holdings] = useState<HoldingStock[]>([]);
  const [marketOpen, setMarketOpen] = useState<boolean | null>(null);
  const [mode, setMode] = useState<'prod' | 'vps'>('prod');

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        setMarketOpen(data.market_open ?? false);
        setMode(data.mode ?? 'prod');
      })
      .catch(() => setMarketOpen(false));
  }, []);

  return (
    <div className="app">
      <Header portfolio={portfolio} marketOpen={marketOpen} mode={mode} />
      <main className="main">
        <section className="panel panel-watch">
          <h2 className="panel-title">관심종목</h2>
          <div className="card-list">
            {watchList.map((stock) => (
              <WatchCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
        <section className="panel panel-holdings">
          <h2 className="panel-title">매수종목</h2>
          <div className="card-list">
            {holdings.map((stock) => (
              <HoldingCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
