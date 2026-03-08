export interface WatchStock {
  code: string;
  name: string;
  currentPrice: number;
  changeRate: number;
  volume: number;
  volumeRate: number;
  scannedAt: string;
}

export interface HoldingStock {
  code: string;
  name: string;
  avgPrice: number;
  currentPrice: number;
  quantity: number;
  profitRate: number;
  profitAmount: number;
  evalAmount: number;
}

export interface PortfolioSummary {
  totalInvested: number;
  totalValue: number;
  dailyProfitRate: number;
  dailyProfitAmount: number;
  cashBalance: number;
}
