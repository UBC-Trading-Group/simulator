import { Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/index';
import TradesPage from './pages/trades';
import LoginPage from './pages/login';
import ProfilePage from './pages/profile';
import PortfolioPage from './pages/portfolio';
import TransactionsPage from './pages/transactions';
import OrderBookPage from './pages/orderbook';
import NewsPage from './pages/news';
import SettingsPage from './pages/settings';
import HelpPage from './pages/help';
import TradingPage from './pages/trading';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import './App.css';

function App() {
  const location = useLocation();
  const isAuthPage = location.pathname === '/login';

  return (
    <AuthProvider>
      <WebSocketProvider>
        <div>
          {!isAuthPage && <Header />}
          <main className={isAuthPage ? 'main auth-main' : 'main container'}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/trades" element={<TradesPage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
              <Route path="/transactions" element={<TransactionsPage />} />
              <Route path="/orderbook" element={<OrderBookPage />} />
              <Route path="/news" element={<NewsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/help" element={<HelpPage />} />
              <Route path="/trade" element={<TradingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Routes>
          </main>
        </div>
      </WebSocketProvider>
    </AuthProvider>
  );
}

export default App;
