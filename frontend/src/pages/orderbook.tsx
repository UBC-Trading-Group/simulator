import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useOrderbook } from "../hooks/useOrderbook";
import { useInstruments } from "../hooks/useInstruments";

function OrderBookPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

  const { instruments } = useInstruments();

  const [search, setSearch] = useState("");
  const [activeTicker, setActiveTicker] = useState("");
  const { bids, asks, isLoading, isError, ticker } = useOrderbook(activeTicker);
  const limitedBids = bids.slice(0, 10);
  const limitedAsks = asks.slice(0, 10);

  // Initialize to first instrument when available
  useEffect(() => {
    if (!activeTicker && instruments.length > 0) {
      setSearch(instruments[0].id);
      setActiveTicker(instruments[0].id);
    }
  }, [instruments, activeTicker]);

  const applyFilter = () => {
    const next = search.trim().toUpperCase();
    if (next) setActiveTicker(next);
  };

  const formatPrice = (p?: number) =>
    p != null ? `$${p.toFixed(2)}` : "--";

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
        <div className="orderbook-header">
          <h1 className="page-title">Order Book</h1>
          <div className="orderbook-actions">
            <div className="orderbook-search">
              <select
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              >
                {instruments.map((inst) => (
                  <option key={inst.id} value={inst.id}>
                    {inst.id} — {inst.full_name}
                  </option>
                ))}
              </select>
              <button onClick={applyFilter}>Apply</button>
            </div>
          </div>
        </div>

        <div className="orderbook-grid">
          <div className="orderbook-side">
            <div className="orderbook-side-head">BID</div>
            <div className="orderbook-table-head">
              <span>Name</span>
              <span className="text-center">Quantity</span>
              <span className="text-right">Price</span>
            </div>
            {isLoading && <div className="orderbook-row muted">Loading…</div>}
            {isError && <div className="orderbook-row muted" style={{ color: "#b91c1c" }}>Ticker "{ticker}" not found.</div>}
            {!isLoading && !limitedBids.length && !isError && (
              <div className="orderbook-row muted">No bids yet.</div>
            )}
            {limitedBids.map((order, idx) => (
              <div className="orderbook-row" key={`bid-${idx}`}>
                <div className="orderbook-name">
                  <div className="orderbook-avatar">{order.ticker.slice(0, 3)}</div>
                  <div>
                    <div className="orderbook-ticker">{order.ticker}</div>
                    <div className="orderbook-sub">Instrument</div>
                  </div>
                </div>
                <span className="text-center">{order.quantity}</span>
                <span className="text-right bid">{formatPrice(order.price)}</span>
              </div>
            ))}
          </div>

          <div className="orderbook-side">
            <div className="orderbook-side-head ask">ASK</div>
            <div className="orderbook-table-head">
              <span>Name</span>
              <span className="text-center">Quantity</span>
              <span className="text-right">Price</span>
            </div>
            {isLoading && <div className="orderbook-row muted">Loading…</div>}
            {isError && <div className="orderbook-row muted" style={{ color: "#b91c1c" }}>Ticker "{ticker}" not found.</div>}
            {!isLoading && !limitedAsks.length && !isError && (
              <div className="orderbook-row muted">No asks yet.</div>
            )}
            {limitedAsks.map((order, idx) => (
              <div className="orderbook-row" key={`ask-${idx}`}>
                <div className="orderbook-name">
                  <div className="orderbook-avatar">{order.ticker.slice(0, 3)}</div>
                  <div>
                    <div className="orderbook-ticker">{order.ticker}</div>
                    <div className="orderbook-sub">Instrument</div>
                  </div>
                </div>
                <span className="text-center">{order.quantity}</span>
                <span className="text-right ask">{formatPrice(order.price)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrderBookPage;
