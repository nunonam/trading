import type { PortfolioSummary } from '../types/stock';

interface HeaderProps {
  portfolio: PortfolioSummary;
}

function formatKRW(value: number): string {
  return value.toLocaleString('ko-KR');
}

export default function Header({ portfolio }: HeaderProps) {
  const { dailyProfitRate, dailyProfitAmount, totalValue, cashBalance } = portfolio;
  const isProfit = dailyProfitRate >= 0;

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">Day Trading</h1>
      </div>
      <div className="header-right">
        <div className="header-stat">
          <span className="header-label">평가금</span>
          <span className="header-value">{formatKRW(totalValue)}원</span>
        </div>
        <div className="header-stat">
          <span className="header-label">예수금</span>
          <span className="header-value">{formatKRW(cashBalance)}원</span>
        </div>
        <div className={`header-profit ${isProfit ? 'profit-up' : 'profit-down'}`}>
          <span className="header-label">일간 수익률</span>
          <span className="header-profit-value">
            {isProfit ? '+' : ''}{dailyProfitRate.toFixed(2)}%
          </span>
          <span className="header-profit-amount">
            ({isProfit ? '+' : ''}{formatKRW(dailyProfitAmount)}원)
          </span>
        </div>
      </div>
    </header>
  );
}
