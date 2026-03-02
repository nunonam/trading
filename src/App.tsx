import Header from './components/Header';
import WatchCard from './components/WatchCard';
import HoldingCard from './components/HoldingCard';
import { mockPortfolio, mockWatchList, mockHoldings } from './data/mock';
import './App.css';

export default function App() {
  return (
    <div className="app">
      <Header portfolio={mockPortfolio} />
      <main className="main">
        <section className="panel panel-watch">
          <h2 className="panel-title">관심종목</h2>
          <div className="card-list">
            {mockWatchList.map((stock) => (
              <WatchCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
        <section className="panel panel-holdings">
          <h2 className="panel-title">매수종목</h2>
          <div className="card-list">
            {mockHoldings.map((stock) => (
              <HoldingCard key={stock.code} stock={stock} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
