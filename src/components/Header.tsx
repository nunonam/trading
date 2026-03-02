import type { PortfolioSummary } from '../types/stock';

interface HeaderProps {
  portfolio: PortfolioSummary;
  marketOpen: boolean | null;
  mode: 'prod' | 'vps';
}

function formatKRW(value: number): string {
  return value.toLocaleString('ko-KR');
}

export default function Header({ portfolio, marketOpen, mode }: HeaderProps) {
  const { dailyProfitRate, dailyProfitAmount, totalValue, cashBalance } = portfolio;
  const isProfit = dailyProfitRate >= 0;

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title"><span className="title-bold">DISTONE</span> <span className="title-light">TRADING</span></h1>
        <span className={`market-status ${mode === 'vps' ? 'mode-paper' : 'mode-prod'}`}>
          {mode === 'vps' ? '모의투자' : '실전투자'}
        </span>
        <span className={`market-status ${marketOpen ? 'market-open' : 'market-closed'}`}>
          {marketOpen === null ? '...' : marketOpen ? '장중' : '장외'}
        </span>
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
