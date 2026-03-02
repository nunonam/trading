import type { WatchStock } from '../types/stock';

interface WatchCardProps {
  stock: WatchStock;
}

function formatKRW(value: number): string {
  return value.toLocaleString('ko-KR');
}

export default function WatchCard({ stock }: WatchCardProps) {
  const { name, code, price, changeRate, signal, addedAt } = stock;
  const isUp = changeRate >= 0;

  return (
    <div className={`card watch-card ${signal.buySignal ? 'buy-signal' : ''}`}>
      <div className="card-header">
        <div className="card-title">
          <span className="stock-name">{name}</span>
          <span className="stock-code">{code}</span>
        </div>
        <span className="card-time">{addedAt}</span>
      </div>

      <div className="card-price">
        <span className="current-price">{formatKRW(price.current)}원</span>
        <span className={`change-rate ${isUp ? 'up' : 'down'}`}>
          {isUp ? '+' : ''}{changeRate.toFixed(2)}%
        </span>
      </div>

      <div className="card-bar">
        <span className="bar-item">고 {formatKRW(price.high)}</span>
        <span className="bar-item">저 {formatKRW(price.low)}</span>
        <span className="bar-item">거래량 {formatKRW(price.volume)}</span>
      </div>

      <div className="card-signals">
        <span className={`signal-badge ${signal.aboveVwap ? 'active' : ''}`}>
          VWAP {formatKRW(signal.vwap)}
        </span>
        <span className={`signal-badge ${signal.emaCross === 'golden' ? 'active' : ''}`}>
          EMA {signal.emaCross === 'golden' ? 'Golden' : signal.emaCross === 'dead' ? 'Dead' : '-'}
        </span>
      </div>

      {signal.buySignal && (
        <div className="card-action">
          <button className="btn btn-buy">매수</button>
        </div>
      )}
    </div>
  );
}
