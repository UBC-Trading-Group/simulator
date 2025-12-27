import { useLocation, useNavigate } from "react-router-dom";

const overviewText =
  "The Trading Simulation places participants in the role of active portfolio managers navigating a dynamic equity market. Participants trade a small set of correlated stocks and an index under conditions of uncertainty, reacting to periodic news events and market shocks. Their objective is to generate profits through precise trade execution, risk management, and interpretation of macro and firm-specific information. Throughout the simulation, stock prices fluctuate in response to underlying market factors and randomized news releases. Each asset has a unique beta to the market index, creating opportunities for relative-value and directional strategies. Participants must decide when to take or hedge exposure, manage volatility, and respond quickly to evolving information. As rounds progress, volatility, correlations, and spreads change—mirroring real-world market conditions where trader psychology and liquidity shape price movements. Performance is measured by final portfolio value over 5 rounds, rewarding consistent profitability and effective risk control under time pressure.";

const descriptionIntro =
  "Each participant begins with a fixed amount of capital, $1,000,000, and trades a diversified set of five stocks and one market index within the TG5 universe, each exhibiting distinct sensitivities to overall market movements.";

const descriptionNotes =
  "Below is a table of characteristics of the five stocks. These 5 stocks follow geometric brownian motion with shifts in drift from news events, and are modelled after a CAPM-like model to the index.";

function HelpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

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
          <button className="active" onClick={() => navigate("/help")}>Help</button>
          <button onClick={() => navigate("/login?mode=login")}>Logout</button>
        </div>
      </aside>

      <div className="dash-main">
        <div className="page-card help-card-shell">
          <header className="help-header">
            <h1 className="help-title">Help: Setup and Information</h1>
          </header>

          <div className="help-content">
            <section className="help-section">
              <h2 className="help-subhead">Overview</h2>
              <p className="help-body">{overviewText}</p>
            </section>

            <section className="help-section">
              <h2 className="help-subhead">Description</h2>
              <p className="help-body">{descriptionIntro}</p>
              <p className="help-body">{descriptionNotes}</p>
            </section>

          </div>
        </div>
      </div>
    </div>
  );
}

export default HelpPage;
