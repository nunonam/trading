import type { WatchStock } from '../types/stock';

interface WatchCardProps {
  stock: WatchStock;
}

function formatKRW(value: number): string {
  return value.toLocaleString('ko-KR');
}

export default function WatchCard({ stock }: WatchCardProps) {
  const { name, code, currentPrice, changeRate, volume, volumeRate, scannedAt } = stock;
  const isUp = changeRate >= 0;

  return (
    <div className="card watch-card">
      <div className="card-header">
        <div className="card-title">
          <span className="stock-name">{name}</span>
          <span className="stock-code">{code}</span>
        </div>
        <span className="card-time">{scannedAt}</span>
      </div>

      <div className="card-price">
        <span className="current-price">{formatKRW(currentPrice)}원</span>
        <span className={`change-rate ${isUp ? 'up' : 'down'}`}>
          {isUp ? '+' : ''}{changeRate.toFixed(2)}%
        </span>
      </div>

      <div className="card-bar">
        <span className="bar-item">거래량 {formatKRW(volume)}</span>
        <span className="bar-item">거래량비 {volumeRate.toFixed(1)}%</span>
      </div>

      <div className="card-action">
        <button className="btn btn-buy">매수</button>
      </div>
    </div>
  );
}
