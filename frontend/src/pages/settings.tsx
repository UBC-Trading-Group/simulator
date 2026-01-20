import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface UserProfile {
  id: number;
  username: string;
  email: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
  first_name?: string | null;
  last_name?: string | null;
  full_name?: string | null;
}

function SettingsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, token, isAuthenticated } = useAuth();
  const isActive = (path: string) => location.pathname === path;

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!isAuthenticated || !user || !token) return;
      try {
        setError(null);
        const res = await fetch(`${API_BASE_URL}/users/${user.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          setError("Could not load profile");
          return;
        }
        const data = await res.json();
        setProfile(data);
      } catch (e) {
        setError("Could not load profile");
      }
    };
    fetchProfile();
  }, [isAuthenticated, user, token]);

  const formatDate = (dt?: string | null) =>
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
        <div className="page-card settings-card">
          <div className="settings-head">
            <div>
              <h1 className="page-title">Settings</h1>
              <p className="settings-subtitle">Account Information</p>
              <p className="settings-subtext">Update your account information</p>
            </div>
          </div>

          {!isAuthenticated && (
            <div className="settings-section">
              <p className="settings-subtext">Log in to view your account details.</p>
              <button className="settings-edit" type="button" onClick={() => navigate("/login?mode=login")}>
                Go to Login
              </button>
            </div>
          )}

          {isAuthenticated && (
            <section className="settings-section">
              <h3 className="settings-section-title">Personal Information</h3>
              {error && <p className="settings-error">{error}</p>}
              <div className="settings-grid">
                <div className="settings-field">
                  <label>First Name</label>
                  <input type="text" value={profile?.first_name ?? ""} readOnly placeholder="First name" />
                </div>
                <div className="settings-field">
                  <label>Last Name</label>
                  <input type="text" value={profile?.last_name ?? ""} readOnly placeholder="Last name" />
                </div>
                <div className="settings-field">
                  <label>Full Name</label>
                  <input type="text" value={profile?.full_name ?? ""} readOnly placeholder="Full name" />
                </div>
                <div className="settings-field">
                  <label>Username</label>
                  <input type="text" value={profile?.username ?? ""} readOnly />
                </div>
                <div className="settings-field">
                  <label>Email</label>
                  <input type="email" value={profile?.email ?? ""} readOnly />
                </div>
                <div className="settings-field">
                  <label>Status</label>
                  <input type="text" value={profile?.is_active ? "Active" : "Inactive"} readOnly />
                </div>
                <div className="settings-field">
                  <label>Role</label>
                  <input type="text" value={profile?.is_superuser ? "Admin" : "User"} readOnly />
                </div>
                <div className="settings-field">
                  <label>Created</label>
                  <input type="text" value={formatDate(profile?.created_at)} readOnly />
                </div>
                <div className="settings-field">
                  <label>Last Updated</label>
                  <input type="text" value={formatDate(profile?.updated_at)} readOnly />
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
