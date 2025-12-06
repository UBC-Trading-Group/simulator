import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import PriceChart from "../components/widgets/chart";
import { useAuth } from "../contexts/AuthContext";

const leaderboard = [
  { name: "Team Cup", change: "+$435.00", positive: true },
  { name: "Team Lebron", change: "+$132.00", positive: true },
  { name: "Moinul Hasan Nayem", change: "-$826.00", positive: false },
  { name: "Dr. Jubed Ahmed", change: "-$1,435.90", positive: false },
  { name: "AR Jakir Alp", change: "-$2,228.00", positive: false },
];

const recentOrders = [
  { ticker: "NOVA", company: "NovaScala Systems Inc.", shares: 23, amount: "$420.84", date: "14 Apr 2022" },
  { ticker: "GENX", company: "Genexa Biotechnologies", shares: 23, amount: "$100.00", date: "05 Apr 2022" },
  { ticker: "AURA", company: "Aurora Financial Group", shares: 23, amount: "$244.20", date: "02 Apr 2022" },
];

interface Position {
  symbol: string;
  full_name: string;
  sector: string;
  quantity: number;
  price: number;
  total_position: number;
  pnl: number;
  pnl_percentage: number;
}

interface PortfolioData {
  positions: Position[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function TradesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  const { token, isAuthenticated } = useAuth();
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);

  // Fetch a lightweight portfolio snapshot for the dashboard card
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const fetchPortfolio = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/portfolio/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        if (!response.ok) return;
        const data = await response.json();
        setPortfolio(data);
      } catch (err) {
        console.error("Failed to load portfolio", err);
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 4000);
    return () => clearInterval(interval);
  }, [isAuthenticated, token]);

  const portfolioRows = portfolio?.positions?.slice(0, 5) ?? [];

  return (
    <div className="dashboard-shell">
      <aside className="dash-sidebar">
        <div className="dash-logo">
          <img src="/logo.png" alt="Trading Group" />
        </div>
        <nav className="dash-nav">
          <button className={isActive("/trades") ? "active" : ""} onClick={() => navigate("/trades")}>Dashboard</button>
          <button className={isActive("/portfolio") ? "active" : ""} onClick={() => navigate("/portfolio")}>Portfolio</button>
          <button className={isActive("/transactions") ? "active" : ""} onClick={() => navigate("/transactions")}>Transactions</button>
          <button className={isActive("/orderbook") ? "active" : ""} onClick={() => navigate("/orderbook")}>Order Book</button>
          <button className={isActive("/news") ? "active" : ""} onClick={() => navigate("/news")}>News</button>
          <button className={isActive("/settings") ? "active" : ""} onClick={() => navigate("/settings")}>Settings</button>
        </nav>
        <div className="dash-nav muted">
          <button onClick={() => navigate("/help")}>Help</button>
          <button onClick={() => navigate("/login?mode=login")}>Logout</button>
        </div>
      </aside>

      <div className="dash-main">
        <header className="dash-header">
          <div>
            <h1>Dashboard</h1>
          </div>
          <div className="dash-actions">
            <button className="pill-btn">Add Widgets</button>
          </div>
        </header>

        <section className="dash-metrics">
          <div className="metric-card metric-dark">
            <div className="metric-label">Realized P&L</div>
            <div className="metric-value">$5240.21</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Volume Traded</div>
            <div className="metric-value">$250.9k</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Current Position</div>
            <div className="metric-value">2</div>
          </div>
        </section>

        <div className="dash-grid">
          <div className="dash-col">
            <section className="dash-card chart-card">
              <div className="card-head">
                <h3>Stock Chart</h3>
              </div>
              <div style={{ height: 320 }}>
                <PriceChart />
              </div>
            </section>

            <section className="dash-card">
              <div className="card-head">
                <h3>Recent Orders</h3>
                <button className="link-button">View All</button>
              </div>
              <div className="orders-table">
                <div className="orders-header">
                  <span>Instrument</span>
                  <span>No. of Shares</span>
                  <span className="text-right">Amount</span>
                  <span className="text-right">Date</span>
                </div>
                {recentOrders.map((order) => (
                  <div className="orders-row" key={`${order.ticker}-${order.date}`}>
                    <div>
                      <div className="order-ticker">{order.ticker}</div>
                      <div className="order-company">{order.company}</div>
                    </div>
                    <div>{order.shares}</div>
                    <div className="text-right">{order.amount}</div>
                    <div className="text-right">{order.date}</div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="dash-col slim">
            <section className="dash-card">
              <div className="card-head">
                <h3>Leaderboard</h3>
                <button className="link-button">View All</button>
              </div>
              <ol className="leaderboard-list">
                {leaderboard.map((entry, idx) => (
                  <li key={entry.name}>
                    <span className="rank">{idx + 1}.</span>
                    <span className="leader-name">{entry.name}</span>
                    <span className={entry.positive ? "pos" : "neg"}>{entry.change}</span>
                  </li>
                ))}
              </ol>
            </section>

            <section className="dash-card">
              <div className="card-head">
                <h3>Portfolio</h3>
                <button className="link-button">View All</button>
              </div>
              {isAuthenticated ? (
                <div className="portfolio-list">
                  {portfolioRows.length === 0 ? (
                    <div className="orders-row" style={{ borderBottom: "none" }}>No positions yet.</div>
                  ) : (
                    portfolioRows.map((item) => {
                      const changePositive = item.pnl >= 0;
                      return (
                        <div className="portfolio-row" key={item.symbol}>
                          <div className="portfolio-ticker">{item.symbol}</div>
                          <div className={`portfolio-change ${changePositive ? "pos" : "neg"}`}>
                            {`${changePositive ? "+" : "-"}$${Math.abs(item.pnl).toFixed(2)}`}
                          </div>
                          <div className="portfolio-balance">${item.total_position.toFixed(2)}</div>
                        </div>
                      );
                    })
                  )}
                </div>
              ) : (
                <div style={{ fontSize: 14, color: "#6b7280" }}>Log in to view your portfolio.</div>
              )}
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TradesPage;
