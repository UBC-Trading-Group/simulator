import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface OrderHistory {
  order_id: string;
  symbol: string;
  quantity: number;
  price?: number;
  type: string;
  created_at?: string;
}

function TransactionsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, isAuthenticated } = useAuth();
  const isActive = (path: string) => location.pathname === path;

  const [orders, setOrders] = useState<OrderHistory[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchOrders = async () => {
      if (!isAuthenticated || !token) {
        setOrders([]);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${API_BASE_URL}/trading/orders`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          setError("Could not load transactions");
          setOrders([]);
          return;
        }
        const data = await res.json();
        if (Array.isArray(data)) {
          // If created_at exists, sort descending by time
          const sorted = [...data].sort((a, b) => {
            const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
            const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
            return tb - ta;
          });
          setOrders(sorted);
        } else {
          setOrders([]);
        }
      } catch (e) {
        setError("Could not load transactions");
        setOrders([]);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
    const id = setInterval(fetchOrders, 5000);
    return () => clearInterval(id);
  }, [isAuthenticated, token]);

  const formatDate = (dt?: string) =>
    dt ? new Date(dt).toLocaleString() : "--";

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
        <h1 className="page-title">Transactions</h1>
        <div className="page-card">
          {!isAuthenticated && (
            <p style={{ color: "#6b7280" }}>Log in to view your order history.</p>
          )}

          {isAuthenticated && (
            <div className="tx-table">
              <div className="tx-row tx-head">
                <span>Stock</span>
                <span>Time</span>
                <span className="text-center">Quantity</span>
                <span className="text-right">Price</span>
                <span className="text-center">Order Type</span>
              </div>
              {error && <div className="tx-row tx-error">{error}</div>}
              {loading && !orders.length && <div className="tx-row">Loading...</div>}
              {!loading && !error && orders.length === 0 && (
                <div className="tx-row">No orders yet.</div>
              )}
              {!error &&
                orders.map((order) => (
                  <div className="tx-row" key={order.order_id}>
                    <span className="tx-strong">{order.symbol}</span>
                    <span>{formatDate(order.created_at)}</span>
                    <span className="text-center">{order.quantity}</span>
                    <span className="text-right">
                      {order.price != null ? `$${order.price.toFixed(2)}` : "--"}
                    </span>
                    <span className="text-center tx-type">
                      {order.type?.toUpperCase?.() ?? "--"}
                    </span>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TransactionsPage;
