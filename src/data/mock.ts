import type { WatchStock, HoldingStock, PortfolioSummary } from '../types/stock';

export const mockPortfolio: PortfolioSummary = {
  totalInvested: 10_000_000,
  totalValue: 10_235_000,
  dailyProfitRate: 2.35,
  dailyProfitAmount: 235_000,
  cashBalance: 5_000_000,
};

export const mockWatchList: WatchStock[] = [
  {
    code: '005930',
    name: '삼성전자',
    price: { current: 82_500, open: 81_000, high: 83_200, low: 80_800, prevClose: 81_200, volume: 12_500_000 },
    changeRate: 1.6,
    signal: { vwap: 81_900, ema9: 82_100, ema20: 81_500, aboveVwap: true, emaCross: 'golden', buySignal: true },
    addedAt: '09:15',
  },
  {
    code: '000660',
    name: 'SK하이닉스',
    price: { current: 178_500, open: 175_000, high: 180_000, low: 174_500, prevClose: 174_000, volume: 5_800_000 },
    changeRate: 2.59,
    signal: { vwap: 177_200, ema9: 178_000, ema20: 176_800, aboveVwap: true, emaCross: 'golden', buySignal: true },
    addedAt: '09:20',
  },
  {
    code: '035720',
    name: '카카오',
    price: { current: 45_300, open: 44_500, high: 45_800, low: 44_200, prevClose: 44_600, volume: 3_200_000 },
    changeRate: 1.57,
    signal: { vwap: 45_100, ema9: 45_000, ema20: 45_200, aboveVwap: true, emaCross: 'none', buySignal: false },
    addedAt: '09:35',
  },
  {
    code: '006400',
    name: '삼성SDI',
    price: { current: 395_000, open: 388_000, high: 398_000, low: 387_000, prevClose: 389_000, volume: 890_000 },
    changeRate: 1.54,
    signal: { vwap: 392_500, ema9: 394_000, ema20: 391_000, aboveVwap: true, emaCross: 'golden', buySignal: true },
    addedAt: '09:40',
  },
];

export const mockHoldings: HoldingStock[] = [
  {
    code: '005930',
    name: '삼성전자',
    avgPrice: 81_200,
    currentPrice: 82_500,
    quantity: 80,
    totalQuantity: 120,
    profitRate: 1.6,
    profitAmount: 104_000,
    status: 'partial_sell',
    swingHigh: 83_200,
    swingLow: 81_000,
  },
  {
    code: '000660',
    name: 'SK하이닉스',
    avgPrice: 176_000,
    currentPrice: 178_500,
    quantity: 10,
    totalQuantity: 10,
    profitRate: 1.42,
    profitAmount: 25_000,
    status: 'holding',
    swingHigh: 180_000,
    swingLow: 175_500,
  },
];
