import { Link, useNavigate } from 'react-router-dom';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { useAuth } from '../contexts/AuthContext';
import LatencyPill from './LatencyPill';
import logoUrl from '/logo.png';
import { ModeToggle } from './mode-toggle';

function Header() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const { latencyMs, isConnected, isReconnecting } = useWebSocketContext();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="app-header dark:bg-dark">
      <div className="header-inner dark:bg-dark">
        <div className="club">
          <Link to="/" className="club-link">
            <img src={logoUrl} alt="" className="club-logo dark:hidden" />
            <img src="/logo-white.png" alt="" className="club-logo hidden dark:block" />
            <span className="club-text dark:text-text-1-dark!">Trading Simulator</span>
          </Link>
        </div>
        <div className="header-actions">
          <LatencyPill
            latencyMs={latencyMs}
            isConnected={isConnected}
            isReconnecting={isReconnecting}
          />
          <Link to="/trades" className="nav-link dark:text-text-1-dark! dark:hover:text-tg-brightred!">Trades</Link>
          <ModeToggle />
          {isAuthenticated ? (
            <div className="auth-actions">
              <Link to="/profile" className="btn btn-secondary">Profile</Link>
              <button className="btn btn-outline" onClick={handleLogout}>Log Out</button>
            </div>
          ) : (
            <div className="auth-actions">
              <button className="btn btn-primary" onClick={() => navigate('/login?mode=login')}>Log In</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
