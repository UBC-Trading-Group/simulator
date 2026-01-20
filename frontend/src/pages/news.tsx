import { useLocation, useNavigate } from "react-router-dom";
import { useNews } from "../hooks/useNews";
import { useAuth } from "../contexts/AuthContext";

function NewsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { news, isLoading, isError } = useNews();
  const isActive = (path: string) => location.pathname === path;

  const formatDate = (tsMs: number) =>
    tsMs ? new Date(tsMs).toLocaleString() : "--";

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
                <h3>Active & Upcoming News</h3>
                <div className="news-meta">
                  {isLoading && <span>Loading…</span>}
                  {isError && <span style={{ color: "#b91c1c" }}>Could not load news</span>}
                </div>
              </div>
              <div className="news-list">
                {(!news || news.length === 0) && !isLoading && !isError && (
                  <div className="news-item empty">No news at the moment.</div>
                )}
                {news.map((item) => (
                  <div className="news-item" key={item.id}>
                    <div className="news-time">{formatDate(item.ts_release_ms)}</div>
                    <div className="news-body">
                      <h4 className="news-title">{item.headline}</h4>
                      <p className="news-desc">{item.description}</p>
                      <div className="news-tags">
                        <span className="news-tag">ID {item.id}</span>
                        {item.decay_halflife_s != null && (
                          <span className="news-tag">Halflife: {item.decay_halflife_s}s</span>
                        )}
                        {item.magnitude_top != null && (
                          <span className="news-tag">Impact: {item.magnitude_top}</span>
                        )}
                      </div>
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
