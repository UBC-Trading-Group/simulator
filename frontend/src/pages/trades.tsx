import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import PriceChart from "../components/widgets/chart";
import LeaderboardWidget from "../components/widgets/LeaderboardWidget";
import PortfolioWidget from "../components/widgets/PortfolioWidget";
import NewsFeedWidget from "../components/widgets/NewsFeedWidget";
import StocksWidget from "../components/widgets/StocksWidget";
import OrderbookWidget from "../components/widgets/OrderbookWidget";
import BuySellWidget from "../components/widgets/BuySellWidget";

type WidgetType =
  | "Leaderboard"
  | "Portfolio"
  | "News Feed"
  | "Stocks"
  | "Orderbook"
  | "Buy/Sell Widget"
  | "Price Chart";

interface WidgetModel {
  id: string;
  type: WidgetType;
  x: number;
  y: number;
  width: number;
  height: number;
  z: number;
}

function useZIndex() {
  const counter = useRef(10);
  const next = () => {
    counter.current += 1;
    return counter.current;
  };
  return { next };
}

function TradesPage() {
  const [widgets, setWidgets] = useState<WidgetModel[]>([]);
  const { next } = useZIndex();

  const widgetTitles: Record<WidgetType, string> = useMemo(
    () => ({
      "Leaderboard": "Leaderboard",
      "Portfolio": "Portfolio",
      "News Feed": "News Feed",
      "Stocks": "Stocks",
      "Orderbook": "Orderbook",
      "Buy/Sell Widget": "Buy / Sell",
      "Price Chart": "Price Chart",
    }),
    []
  );

  const addWidget = useCallback((type: WidgetType) => {
    setWidgets(prev => {
      const offset = prev.length * 16;
      const id = `${type}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      const base: WidgetModel = {
        id,
        type,
        x: 120 + (offset % 180),
        y: 60 + (offset % 120),
        width: 420,
        height: 280,
        z: next(),
      };
      return [...prev, base];
    });
  }, [next]);

  const closeWidget = useCallback((id: string) => {
    setWidgets(prev => prev.filter(w => w.id !== id));
  }, []);

  const updateWidget = useCallback((id: string, partial: Partial<WidgetModel>) => {
    setWidgets(prev => prev.map(w => (w.id === id ? { ...w, ...partial } : w)));
  }, []);

  return (
    <div className="trades">
      <aside className="overlay-aside">
        <h3 className="overlay-title">Widgets</h3>
        <ul className="widgets-list">
          <li onClick={() => addWidget("Price Chart")}>Price Chart</li>
          <li onClick={() => addWidget("Buy/Sell Widget")}>Buy/Sell Widget</li>
          <li onClick={() => addWidget("Portfolio")}>Portfolio</li>
          <li onClick={() => addWidget("Leaderboard")}>Leaderboard</li>
          <li onClick={() => addWidget("News Feed")}>News Feed</li>
          <li onClick={() => addWidget("Stocks")}>Stocks</li>
          <li onClick={() => addWidget("Orderbook")}>Orderbook</li>
        </ul>
      </aside>

      <div className="trades-stage">
        {widgets.map(w => (
          <WidgetWindow
            key={w.id}
            id={w.id}
            title={widgetTitles[w.type]}
            x={w.x}
            y={w.y}
            width={w.width}
            height={w.height}
            z={w.z}
            onFocus={() => updateWidget(w.id, { z: next() })}
            onMove={(x, y) => updateWidget(w.id, { x, y })}
            onResize={(width, height) => updateWidget(w.id, { width, height })}
            onClose={() => closeWidget(w.id)}
          >
            <WidgetBody type={w.type} />
          </WidgetWindow>
        ))}
      </div>
    </div>
  );
}

function WidgetBody({ type }: { type: WidgetType }) {
  if (type === "Price Chart") {
    return <PriceChart />;
  }
  if (type === "Leaderboard") return <LeaderboardWidget />;
  if (type === "Portfolio") return <PortfolioWidget />;
  if (type === "News Feed") return <NewsFeedWidget />;
  if (type === "Stocks") return <StocksWidget />;
  if (type === "Orderbook") return <OrderbookWidget />;
  if (type === "Buy/Sell Widget") return <BuySellWidget />;
  return null;
}

function WidgetWindow(props: {
  id: string;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  z: number;
  onMove: (x: number, y: number) => void;
  onResize: (w: number, h: number) => void;
  onClose: () => void;
  onFocus: () => void;
  children: React.ReactNode;
}) {
  const { id, title, x, y, width, height, z, onMove, onResize, onClose, onFocus, children } = props;
  const ref = useRef<HTMLDivElement | null>(null);
  const dragging = useRef(false);
  const dragOffset = useRef({ dx: 0, dy: 0 });

  const onHeaderMouseDown = (e: React.MouseEvent) => {
    if (!ref.current) return;
    dragging.current = true;
    dragOffset.current = { dx: e.clientX - x, dy: e.clientY - y };
    onFocus();
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  };

  const onMouseMove = (e: MouseEvent) => {
    if (!dragging.current) return;
    const nx = e.clientX - dragOffset.current.dx;
    const ny = e.clientY - dragOffset.current.dy;
    const clampedX = Math.max(0, nx);
    const clampedY = Math.max(0, ny);
    onMove(clampedX, clampedY);
  };

  const onMouseUp = () => {
    dragging.current = false;
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  };

  // Track resizes with ResizeObserver so sizes persist
  useEffect(() => {
  const node = ref.current;
  if (!node) return;

  const ro = new ResizeObserver(entries => {
    const { width: w, height: h } = entries[0].contentRect;

    // prevent jitter / resize loop
    if (Math.abs(w - width) > 2 || Math.abs(h - height) > 2) {
      onResize(Math.round(w), Math.round(h));
    }
  });

  ro.observe(node);
  return () => ro.disconnect();
}, [width, height, onResize]);

  return (
    <div
      ref={el => { ref.current = el; }}
      className="widget-win dark:bg-dark-2!"
      style={{ left: x, top: y, width, height, zIndex: z }}
      onMouseDown={onFocus}
      data-id={id}
    >
      <div className="flex items-center justify-between cursor-move select-none font-bold p-5 bg-white dark:bg-dark-2" onMouseDown={onHeaderMouseDown}>
        <span className="font-semibold text-text-1 dark:text-text-1-dark text-2xl">{title}</span>
        <button className="widget-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      <div className="widget-body">
        {children}
      </div>
    </div>
  );
}

export default TradesPage


