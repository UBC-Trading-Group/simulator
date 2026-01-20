import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import PriceChart from "../components/widgets/chart";
import BuySellWidget from "../components/widgets/BuySellWidget";
import { useAuth } from "../contexts/AuthContext";
import { getApiBaseUrl } from "../config/api";
import { useNews } from "../hooks/useNews";

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
  price?: number;
  created_at?: string;
}

type WidgetKey = "chart" | "recentOrders" | "leaderboard" | "portfolio" | "news";
const ALL_WIDGETS: WidgetKey[] = ["chart", "recentOrders", "leaderboard", "portfolio", "news"];

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
  const [widgetPickerOpen, setWidgetPickerOpen] = useState(false);
  const [visibleWidgets, setVisibleWidgets] = useState<WidgetKey[]>([...ALL_WIDGETS]);
  const { news, isLoading: newsLoading } = useNews();

  const availableToAdd = useMemo(
    () => ALL_WIDGETS.filter((w) => !visibleWidgets.includes(w)),
    [visibleWidgets]
  );

  const hideWidget = (key: WidgetKey) =>
    setVisibleWidgets((prev) => prev.filter((w) => w !== key));
  const showWidget = (key: WidgetKey) =>
    setVisibleWidgets((prev) => (prev.includes(key) ? prev : [...prev, key]));

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
          <button className={isActive("/trade") ? "active" : ""} onClick={() => navigate("/trade")}>Buy / Sell</button>
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
            <div className="widget-picker">
              <button className="pill-btn" onClick={() => setWidgetPickerOpen((o) => !o)}>
                Add Widgets
              </button>
              {widgetPickerOpen && (
                <div className="widget-dropdown">
                  {availableToAdd.map((w) => (
                    <button
                      key={w}
                      className="widget-dropdown-item"
                      onClick={() => {
                        showWidget(w);
                        setWidgetPickerOpen(false);
                      }}
                      >
                        {w === "chart" && "Stock Chart"}
                        {w === "recentOrders" && "Recent Orders"}
                        {w === "leaderboard" && "Leaderboard"}
                        {w === "portfolio" && "Portfolio"}
                        {w === "news" && "News"}
                      </button>
                    ))}
                  {availableToAdd.length === 0 && (
                    <div className="widget-dropdown-empty">All widgets visible</div>
                  )}
                </div>
              )}
            </div>
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
            {visibleWidgets.includes("chart") && (
              <section className="dash-card chart-card">
                <div className="card-head">
                  <h3>Stock Chart</h3>
                  <button className="widget-close" onClick={() => hideWidget("chart")}>×</button>
                </div>
                <div style={{ height: 320 }}>
                  <PriceChart />
                </div>
              </section>
            )}

            {visibleWidgets.includes("recentOrders") && (
              <section className="dash-card">
                <div className="card-head">
                  <h3>Recent Orders</h3>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="link-button" onClick={() => navigate("/transactions")}>View All</button>
                    <button className="widget-close" onClick={() => hideWidget("recentOrders")}>×</button>
                  </div>
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
                      const formattedAmount = amount ? `$${amount.toFixed(2)}` : "--";
                      const dateStr = order.created_at ? new Date(order.created_at).toLocaleDateString() : "--";
                      return (
                        <div className="orders-row" key={order.order_id}>
                          <div>
                            <div className="order-ticker">{order.symbol}</div>
                            <div className="order-company" style={{ textTransform: "capitalize" }}>{order.type}</div>
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
            )}
          </div>

          <BuySellWidget />

          <div className="dash-col slim">
            {visibleWidgets.includes("leaderboard") && (
              <section className="dash-card">
                <div className="card-head">
                  <h3>Leaderboard</h3>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="link-button">View All</button>
                    <button className="widget-close" onClick={() => hideWidget("leaderboard")}>×</button>
                  </div>
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
            )}

            {visibleWidgets.includes("portfolio") && (
              <section className="dash-card">
                <div className="card-head">
                  <h3>Portfolio</h3>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="link-button">View All</button>
                    <button className="widget-close" onClick={() => hideWidget("portfolio")}>×</button>
                  </div>
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
            )}

            {visibleWidgets.includes("news") && (
              <section className="dash-card">
                <div className="card-head">
                  <h3>News</h3>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button className="link-button" onClick={() => navigate("/news")}>View All</button>
                    <button className="widget-close" onClick={() => hideWidget("news")}>×</button>
                  </div>
                </div>
                {newsLoading && <div className="orders-row" style={{ borderBottom: "none" }}>Loading news…</div>}
                {!newsLoading && news.length === 0 && (
                  <div className="orders-row" style={{ borderBottom: "none" }}>No news yet.</div>
                )}
                {!newsLoading && news.length > 0 && (
                  <div className="news-widget-list">
                    {news.slice(0, 4).map((item) => (
                      <div className="news-widget-item" key={item.id}>
                        <div className="news-widget-headline">{item.headline}</div>
                        <div className="news-widget-meta">{new Date(item.ts_release_ms).toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TradesPage;
