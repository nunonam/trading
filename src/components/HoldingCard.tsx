import type { HoldingStock } from '../types/stock';

interface HoldingCardProps {
  stock: HoldingStock;
}

function formatKRW(value: number): string {
  return value.toLocaleString('ko-KR');
}

export default function HoldingCard({ stock }: HoldingCardProps) {
  const { name, code, avgPrice, currentPrice, quantity, profitRate, profitAmount } = stock;
  const isProfit = profitRate >= 0;

  return (
    <div className={`card holding-card ${isProfit ? 'profit' : 'loss'}`}>
      <div className="card-header">
        <div className="card-title">
          <span className="stock-name">{name}</span>
          <span className="stock-code">{code}</span>
        </div>
      </div>

      <div className="card-price">
        <span className="current-price">{formatKRW(currentPrice)}원</span>
        <span className={`change-rate ${isProfit ? 'up' : 'down'}`}>
          {isProfit ? '+' : ''}{profitRate.toFixed(2)}%
        </span>
      </div>

      <div className="holding-detail">
        <div className="detail-row">
          <span className="detail-label">평균단가</span>
          <span className="detail-value">{formatKRW(avgPrice)}원</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">수량</span>
          <span className="detail-value">{quantity}주</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">수익금</span>
          <span className={`detail-value ${isProfit ? 'up' : 'down'}`}>
            {isProfit ? '+' : ''}{formatKRW(profitAmount)}원
          </span>
        </div>
      </div>

      <div className="card-actions">
        <button className="btn btn-sell">매도 10%</button>
        <button className="btn btn-stop">손절</button>
      </div>
    </div>
  );
}
