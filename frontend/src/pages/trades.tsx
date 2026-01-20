import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import PriceChart from "../components/widgets/chart";
import BuySellWidget from "../components/widgets/BuySellWidget";
import { useAuth } from "../contexts/AuthContext";
import { getApiBaseUrl } from "../config/api";
import { useActiveNews, useNewsStatus } from "../hooks/useNews";

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
  filled_quantity?: number;
  type: string;
  price?: number;
  status?: string;
  created_at?: string;
}

type WidgetKey = "chart" | "recentOrders" | "leaderboard" | "portfolio" | "news" | "buySell";

interface Widget {
  id: string;
  type: WidgetKey;
}

const WIDGET_NAMES: Record<WidgetKey, string> = {
  chart: "Stock Chart",
  recentOrders: "Recent Orders",
  leaderboard: "Leaderboard",
  portfolio: "Portfolio",
  news: "News",
  buySell: "Buy / Sell",
};

function TradesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;
  const { token, isAuthenticated } = useAuth();
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [realizedPnL, setRealizedPnL] = useState<number | null>(null);
  const [cashFlow, setCashFlow] = useState<number | null>(null);
  const [marketValue, setMarketValue] = useState<number | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [widgetPickerOpen, setWidgetPickerOpen] = useState(false);
  const [widgets, setWidgets] = useState<Widget[]>([
    { id: "chart-1", type: "chart" },
    { id: "orders-1", type: "recentOrders" },
    { id: "buysell-1", type: "buySell" },
    { id: "leaderboard-1", type: "leaderboard" },
    { id: "portfolio-1", type: "portfolio" },
    { id: "news-1", type: "news" },
  ]);
  const { activeNews, simTimeSeconds, isLoading: newsLoading } = useActiveNews();
  const { status: newsStatus } = useNewsStatus();

  const addWidget = (type: WidgetKey) => {
    const newWidget: Widget = {
      id: `${type}-${Date.now()}`,
      type,
    };
    setWidgets((prev) => [...prev, newWidget]);
    setWidgetPickerOpen(false);
  };

  const removeWidget = (id: string) => {
    setWidgets((prev) => prev.filter((w) => w.id !== id));
  };

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
        
        // Update metrics from backend response
        setRealizedPnL(data.realized_pnl ?? 0);
        setCashFlow(data.cash ?? 0);
        setMarketValue(data.portfolio_market_value ?? 0);
      } catch (err) {
        console.error("Failed to load portfolio", err);
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 500); // Update every 0.5 seconds
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
    const interval = setInterval(fetchOrders, 1000); // Update every 1 second
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

      <div className="dash-main" style={{ padding: '12px', maxWidth: '100%' }}>
        <header className="dash-header" style={{ padding: '12px 0', marginBottom: '12px' }}>
          <div>
            <h1 style={{ margin: 0 }}>Dashboard</h1>
          </div>
          <div className="dash-actions">
            <div className="widget-picker">
              <button className="pill-btn" onClick={() => setWidgetPickerOpen((o) => !o)}>
                Add Widget
              </button>
              {widgetPickerOpen && (
                <div className="widget-dropdown">
                  {Object.entries(WIDGET_NAMES).map(([key, name]) => (
                    <button
                      key={key}
                      className="widget-dropdown-item"
                      onClick={() => addWidget(key as WidgetKey)}
                    >
                      {name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </header>

        <section className="dash-metrics" style={{ gap: '12px', marginBottom: '12px' }}>
          <div className="metric-card metric-dark">
            <div className="metric-label">Realized P&L</div>
            <div className="metric-value">{formatCurrency(realizedPnL)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Cash Balance</div>
            <div className="metric-value">{formatCurrency(cashFlow)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Portfolio Value</div>
            <div className="metric-value">{formatCurrency(marketValue)}</div>
          </div>
        </section>

        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
          gridAutoRows: 'minmax(300px, auto)'
        }}>
          {widgets.map((widget) => {
            // Define size based on widget type
            const getWidgetStyle = (type: WidgetKey) => {
              switch(type) {
                case "chart":
                  return { gridColumn: "span 3", minHeight: "400px" };
                case "buySell":
                  return { gridColumn: "span 1", minHeight: "500px" };
                case "recentOrders":
                  return { gridColumn: "span 2", minHeight: "300px" };
                case "leaderboard":
                case "portfolio":
                case "news":
                  return { gridColumn: "span 1", minHeight: "300px" };
                default:
                  return { gridColumn: "span 1", minHeight: "300px" };
              }
            };
            
            const widgetStyle = getWidgetStyle(widget.type);

            if (widget.type === "chart") {
              return (
                <section key={widget.id} className="dash-card chart-card" style={widgetStyle}>
                  <div className="card-head">
                    <h3>Stock Chart</h3>
                    <button className="widget-close" onClick={() => removeWidget(widget.id)}>×</button>
                  </div>
                  <div style={{ height: 'calc(100% - 50px)', minHeight: 250 }}>
                    <PriceChart />
                  </div>
                </section>
              );
            }

            if (widget.type === "recentOrders") {
              return (
                <section key={widget.id} className="dash-card" style={widgetStyle}>
                  <div className="card-head">
                    <h3>Recent Orders</h3>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="link-button" onClick={() => navigate("/transactions")}>View All</button>
                      <button className="widget-close" onClick={() => removeWidget(widget.id)}>×</button>
                    </div>
                  </div>
                {isAuthenticated ? (
                  <div className="orders-table">
                    <div className="orders-header" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr' }}>
                      <span>Symbol</span>
                      <span>Side</span>
                      <span className="text-right">Shares</span>
                      <span className="text-right">Price</span>
                      <span className="text-right">Status</span>
                    </div>
                    {ordersError && (
                      <div className="orders-row" style={{ borderBottom: "none", color: "#b91c1c" }}>
                        {ordersError}
                      </div>
                    )}
                    {!ordersError && orders.length === 0 && (
                      <div className="orders-row" style={{ borderBottom: "none" }}>No orders yet.</div>
                    )}
                    {!ordersError && orders.length > 0 && orders.slice(0, 10).map((order) => {
                      const statusStyle = {
                        filled: { color: '#10b981', fontWeight: 600 },
                        partially_filled: { color: '#f59e0b', fontWeight: 600 },
                        open: { color: '#6b7280', fontWeight: 400 },
                      }[order.status || 'open'] || {};
                      
                      return (
                        <div className="orders-row" key={order.order_id} style={{ 
                          display: 'grid', 
                          gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr',
                          gap: '8px',
                          padding: '12px 16px'
                        }}>
                          <div className="order-ticker" style={{ fontWeight: 600 }}>{order.symbol}</div>
                          <div style={{ textTransform: "uppercase", fontSize: '12px', color: order.type === 'buy' ? '#10b981' : '#ef4444' }}>
                            {order.type}
                          </div>
                          <div className="text-right">
                            {order.filled_quantity && order.filled_quantity < order.quantity 
                              ? `${order.filled_quantity}/${order.quantity}`
                              : order.quantity}
                          </div>
                          <div className="text-right">${order.price?.toFixed(2) || "--"}</div>
                          <div className="text-right" style={statusStyle}>
                            {order.status?.replace('_', ' ') || 'open'}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div style={{ fontSize: 14, color: "#6b7280" }}>Log in to view recent orders.</div>
                )}
                </section>
              );
            }

            if (widget.type === "buySell") {
              return (
                <div key={widget.id} style={widgetStyle}>
                  <BuySellWidget />
                </div>
              );
            }

            if (widget.type === "leaderboard") {
              return (
                <section key={widget.id} className="dash-card" style={widgetStyle}>
                  <div className="card-head">
                    <h3>Leaderboard</h3>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="link-button">View All</button>
                      <button className="widget-close" onClick={() => removeWidget(widget.id)}>×</button>
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
              );
            }

            if (widget.type === "portfolio") {
              return (
                <section key={widget.id} className="dash-card" style={widgetStyle}>
                  <div className="card-head">
                    <h3>Portfolio</h3>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="link-button">View All</button>
                      <button className="widget-close" onClick={() => removeWidget(widget.id)}>×</button>
                    </div>
                  </div>
                {isAuthenticated ? (
                  <div className="portfolio-list">
                    {portfolioRows.length === 0 ? (
                      <div className="orders-row" style={{ borderBottom: "none" }}>No positions yet.</div>
                    ) : (
                      <>
                        <div style={{ 
                          display: 'grid', 
                          gridTemplateColumns: '1fr 1fr 1fr 1fr', 
                          gap: '8px',
                          padding: '8px 16px',
                          fontSize: '11px',
                          fontWeight: 600,
                          color: '#6b7280',
                          textTransform: 'uppercase',
                          borderBottom: '2px solid #e5e7eb'
                        }}>
                          <div>Symbol</div>
                          <div>Shares</div>
                          <div>P&L</div>
                          <div style={{ textAlign: 'right' }}>Value</div>
                        </div>
                        {portfolioRows.map((item) => {
                        const changePositive = item.pnl >= 0;
                        return (
                          <div className="portfolio-row" key={item.symbol} style={{ 
                            display: 'grid', 
                            gridTemplateColumns: '1fr 1fr 1fr 1fr', 
                            gap: '8px',
                            alignItems: 'center',
                            padding: '12px 16px',
                            borderBottom: '1px solid #e5e7eb'
                          }}>
                            <div className="portfolio-ticker" style={{ fontWeight: 600 }}>{item.symbol}</div>
                            <div style={{ fontSize: '13px', color: '#6b7280' }}>
                              {item.quantity} shares
                            </div>
                            <div className={`portfolio-change ${changePositive ? "pos" : "neg"}`}>
                              {`${changePositive ? "+" : ""}$${item.pnl.toFixed(2)}`}
                            </div>
                            <div className="portfolio-balance" style={{ textAlign: 'right' }}>
                              ${item.total_position.toFixed(2)}
                            </div>
                          </div>
                        );
                        })}
                      </>
                    )}
                  </div>
                ) : (
                  <div style={{ fontSize: 14, color: "#6b7280" }}>Log in to view your portfolio.</div>
                )}
                </section>
              );
            }

            if (widget.type === "news") {
              const formatSimTime = (seconds: number) => {
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${mins}m ${secs}s`;
              };

              return (
                <section key={widget.id} className="dash-card" style={widgetStyle}>
                  <div className="card-head">
                    <h3>News</h3>
                    <div style={{ display: "flex", gap: 8 }}>
                      {newsStatus && (
                        <span style={{ fontSize: "12px", color: "#6b7280", alignSelf: "center" }}>
                          {formatSimTime(newsStatus.sim_time_seconds)}
                        </span>
                      )}
                      <button className="link-button" onClick={() => navigate("/news")}>View All</button>
                      <button className="widget-close" onClick={() => removeWidget(widget.id)}>×</button>
                    </div>
                  </div>
                {newsLoading && <div className="orders-row" style={{ borderBottom: "none" }}>Loading news…</div>}
                {!newsLoading && activeNews.length === 0 && (
                  <div className="orders-row" style={{ borderBottom: "none" }}>No active news.</div>
                )}
                {!newsLoading && activeNews.length > 0 && (
                  <div className="news-widget-list">
                    {activeNews.slice(0, 4).map((item) => (
                      <div className="news-widget-item" key={item.id}>
                        <div className="news-widget-headline">{item.headline}</div>
                      </div>
                    ))}
                  </div>
                )}
                </section>
              );
            }

            return null;
          })}
        </div>
      </div>
    </div>
  );
}

export default TradesPage;
