export interface StockPrice {
  current: number;
  open: number;
  high: number;
  low: number;
  prevClose: number;
  volume: number;
}

export interface TechnicalSignal {
  vwap: number;
  ema9: number;
  ema20: number;
  aboveVwap: boolean;
  emaCross: 'golden' | 'dead' | 'none';
  buySignal: boolean;
}

export interface WatchStock {
  code: string;
  name: string;
  price: StockPrice;
  changeRate: number;
  signal: TechnicalSignal;
  addedAt: string;
}

export interface HoldingStock {
  code: string;
  name: string;
  avgPrice: number;
  currentPrice: number;
  quantity: number;
  totalQuantity: number;
  profitRate: number;
  profitAmount: number;
  status: 'holding' | 'partial_sell' | 'stop_loss';
  swingHigh: number;
  swingLow: number;
}

export interface PortfolioSummary {
  totalInvested: number;
  totalValue: number;
  dailyProfitRate: number;
  dailyProfitAmount: number;
  cashBalance: number;
}
