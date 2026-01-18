import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import PriceChart from "../components/widgets/chart";
import { useAuth } from "../contexts/AuthContext";
import { getApiBaseUrl } from "../config/api";

const leaderboard = [
  { name: "Team Cup", change: "+$435.00", positive: true },
  { name: "Team Lebron", change: "+$132.00", positive: true },
  { name: "Moinul Hasan Nayem", change: "-$826.00", positive: false },
  { name: "Dr. Jubed Ahmed", change: "-$1,435.90", positive: false },
  { name: "AR Jakir Alp", change: "-$2,228.00", positive: false },
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

interface Order {
  order_id: string;
  symbol: string;
  quantity: number;
  type: string;
  status: string;
  price?: number;
  created_at?: string;
}

function TradesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  const { token, isAuthenticated } = useAuth();
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [realizedPnL, setRealizedPnL] = useState<number | null>(null);
  const [volumeTraded, setVolumeTraded] = useState<number | null>(null);
  const [currentPositions, setCurrentPositions] = useState<number | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersError, setOrdersError] = useState<string | null>(null);

  const formatCurrency = (value: number | null) => {
    if (value === null || Number.isNaN(value)) return "--";
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  };

  // Fetch a lightweight portfolio snapshot for the dashboard card
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const fetchPortfolio = async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/portfolio/`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        if (!response.ok) return;
        const data = await response.json();
        setPortfolio(data);
        if (Array.isArray(data.positions)) {
          const totalPnl = data.positions.reduce(
            (acc: number, pos: Position) => acc + (pos.pnl ?? 0),
            0
          );
          const totalVolume = data.positions.reduce(
            (acc: number, pos: Position) => acc + Math.abs(pos.total_position ?? 0),
            0
          );
          setRealizedPnL(totalPnl);
          setVolumeTraded(totalVolume);
          setCurrentPositions(data.positions.length);
        }
      } catch (err) {
        console.error("Failed to load portfolio", err);
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 4000);
    return () => clearInterval(interval);
  }, [isAuthenticated, token]);

  // Fetch recent orders for dashboard table
  useEffect(() => {
    if (!isAuthenticated || !token) {
      setOrders([]);
      return;
    }

    const fetchOrders = async () => {
      try {
        setOrdersError(null);
        const response = await fetch(`${getApiBaseUrl()}/trading/orders`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        if (!response.ok) {
          setOrdersError("Could not load orders");
          return;
        }
        const data = await response.json();
        if (Array.isArray(data)) {
          setOrders(data);
        }
      } catch (err) {
        console.error("Failed to load orders", err);
        setOrdersError("Could not load orders");
      }
    };

    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
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
            <div className="metric-value">{formatCurrency(realizedPnL)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Volume Traded</div>
            <div className="metric-value">{formatCurrency(volumeTraded)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Current Position</div>
            <div className="metric-value">
              {currentPositions !== null ? currentPositions : "--"}
            </div>
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
              {isAuthenticated ? (
                <div className="orders-table">
                  <div className="orders-header">
                    <span>Instrument</span>
                    <span>No. of Shares</span>
                    <span className="text-right">Amount</span>
                    <span className="text-right">Date</span>
                  </div>
                  {ordersError && (
                    <div className="orders-row" style={{ borderBottom: "none", color: "#b91c1c" }}>
                      {ordersError}
                    </div>
                  )}
                  {!ordersError && orders.length === 0 && (
                    <div className="orders-row" style={{ borderBottom: "none" }}>No orders yet.</div>
                  )}
                  {!ordersError && orders.length > 0 && orders.map((order) => {
                    const amount = order.price ? order.price * order.quantity : undefined;
                    const formattedAmount = amount ? `$${amount.toFixed(2)}` : "—";
                    const dateStr = order.created_at ? new Date(order.created_at).toLocaleDateString() : "—";
                    return (
                      <div className="orders-row" key={order.order_id}>
                        <div>
                          <div className="order-ticker">{order.symbol}</div>
                          <div className="order-company" style={{ textTransform: "capitalize" }}>{order.type} • {order.status}</div>
                        </div>
                        <div>{order.quantity}</div>
                        <div className="text-right">{formattedAmount}</div>
                        <div className="text-right">{dateStr}</div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div style={{ fontSize: 14, color: "#6b7280" }}>Log in to view recent orders.</div>
              )}
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

            <section className="dash-card">
            <div className="card-head">
              <h3>Recent News</h3>
              <button className="link-button">View All</button>
            </div>
            {true ? (
              <>
                <div className="flex gap-2 mb-6">
                  {["All", "My Stocks", "Market"].map((label:string) => <>
                    <button className="px-2 py-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 text-xs font-medium">
                        {label}
                    </button>
                    </>)}
                </div>

                <div className="space-y-0">
                  {[0,1].map(()=> (

                    
                    <div className="relative pl-4 py-1 mb-2 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                      <div className="absolute left-0 top-0 w-1 h-full bg-green-500 rounded-full"></div>
                      <div className="flex gap-4">
                          <div className="flex-1 min-w-0">
                              <h3 className="text-xs font-semibold text-gray-800 mb-2 leading-tight">
                                  NOVA shares surge 12% on strong quarterly earnings report
                              </h3>
                              <div className="flex items-center gap-2 mb-1">
                                  <span className="px-2.5 py-0.5 bg-blue-50 text-blue-600 text-xs font-medium rounded-full">
                                      NOVA
                                  </span>
                              </div>
                            <p className="text-xs text-gray-500">Bloomberg • 2 hours ago</p>
                        </div>
                    </div>
                </div>
                  ))}
              </div>
            </>
            ) : (
              <h1>ad</h1>
            )}

             
          </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TradesPage;
