import { useLocation, useNavigate } from "react-router-dom";
import { useActiveNews, useNewsStatus } from "../hooks/useNews";
import { useAuth } from "../contexts/AuthContext";

function NewsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { activeNews, simTimeSeconds, activeCount, isLoading, isError } = useActiveNews();
  const { status: newsStatus } = useNewsStatus();
  const isActive = (path: string) => location.pathname === path;

  const formatSimTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const getImpactColor = (effect: number) => {
    if (effect > 0.01) return "#059669";
    if (effect > 0.005) return "#10b981";
    if (effect < -0.01) return "#dc2626";
    if (effect < -0.005) return "#ef4444";
    return "#f59e0b";
  };

  const getImpactLabel = (effect: number) => {
    const pct = (effect * 100).toFixed(2);
    return effect >= 0 ? `+${pct}%` : `${pct}%`;
  };

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
        <h1 className="page-title">News</h1>
        <div className="page-card">
          {!isAuthenticated && (
            <p style={{ color: "#6b7280" }}>Log in to see current news events.</p>
          )}

          {isAuthenticated && (
            <div className="news-feed">
              <div className="news-head">
                <h3>Active News Events</h3>
                <div className="news-meta">
                  {isLoading && <span>Loading…</span>}
                  {isError && <span style={{ color: "#b91c1c" }}>Could not load news</span>}
                  {!isLoading && !isError && newsStatus && (
                    <span style={{ color: "#6b7280" }}>
                      Simulation Time: {formatSimTime(newsStatus.sim_time_seconds)}
                    </span>
                  )}
                </div>
              </div>
              <div className="news-list">
                {activeCount === 0 && !isLoading && !isError && (
                  <div className="news-item empty">
                    <p>No active news events.</p>
                    <p style={{ fontSize: "14px", color: "#6b7280", marginTop: "8px" }}>
                      News will automatically activate at 100s, 200s, 300s, etc. of simulation time.
                    </p>
                  </div>
                )}
                {activeNews.map((item) => (
                  <div className="news-item" key={item.id}>
                    <div className="news-body">
                      <h4 className="news-title">{item.headline}</h4>
                      <p className="news-desc">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default NewsPage;
