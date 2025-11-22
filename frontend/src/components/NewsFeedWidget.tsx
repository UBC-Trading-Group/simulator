import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface NewsItem {
  id: number;
  headline: string;
  description: string;
}

const newsItems: NewsItem[] = [
  {
    id: 1,
    headline: "Market Opens Higher on Tech Rally",
    description: "Major tech stocks surge as investors show renewed confidence in AI sector growth."
  },
  {
    id: 2,
    headline: "Fed Signals Potential Rate Cut",
    description: "Federal Reserve hints at possible interest rate reduction in next quarter."
  },
  {
    id: 3,
    headline: "Oil Prices Climb on Supply Concerns",
    description: "Crude oil futures rise amid geopolitical tensions in Middle East."
  },
  {
    id: 4,
    headline: "Earnings Beat Expectations",
    description: "Major corporations report stronger than expected Q4 earnings results."
  },
  {
    id: 5,
    headline: "Cryptocurrency Market Volatility",
    description: "Bitcoin and Ethereum experience significant price swings following regulatory news."
  },
  {
    id: 6,
    headline: "Retail Sales Data Released",
    description: "Consumer spending shows resilience despite economic headwinds."
  }
];

interface NewsDetailWidgetProps {
  newsItem: NewsItem;
  x: number;
  y: number;
  width: number;
  height: number;
  z: number;
  onMove: (x: number, y: number) => void;
  onResize: (w: number, h: number) => void;
  onClose: () => void;
  onFocus: () => void;
}

function NewsDetailWidgetWindow({
  newsItem,
  x,
  y,
  width,
  height,
  z,
  onMove,
  onResize,
  onClose,
  onFocus,
}: NewsDetailWidgetProps) {
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

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const ro = new ResizeObserver(entries => {
      const entry = entries[0];
      const cr = entry.contentRect;
      onResize(Math.round(cr.width), Math.round(cr.height));
    });
    ro.observe(node);
    return () => ro.disconnect();
  }, [onResize]);

  const tradesStage = document.querySelector(".trades-stage");
  if (!tradesStage) return null;

  return createPortal(
    <div
      ref={el => { ref.current = el; }}
      className="widget-win"
      style={{ left: x, top: y, width, height, zIndex: z }}
      onMouseDown={onFocus}
    >
      <div className="widget-header" onMouseDown={onHeaderMouseDown}>
        <span className="widget-title">{newsItem.headline}</span>
        <button className="widget-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      <div className="widget-body">
        <div className="p-4 flex flex-col h-full">
          <div className="flex-1 overflow-y-auto text-sm text-gray-700 leading-relaxed">
            <h2 className="text-lg font-bold text-gray-900 mb-4">{newsItem.headline}</h2>
            <p className="text-gray-700">{newsItem.description}</p>
          </div>
        </div>
      </div>
    </div>,
    tradesStage
  );
}

function NewsFeedWidget() {
  const [detailWidget, setDetailWidget] = useState<{
    newsItem: NewsItem;
    x: number;
    y: number;
    width: number;
    height: number;
    z: number;
  } | null>(null);
  const zIndexRef = useRef(100);

  const handleNewsClick = useCallback((item: NewsItem) => {
    const offset = Math.random() * 100;
    setDetailWidget({
      newsItem: item,
      x: 120 + (offset % 180),
      y: 60 + (offset % 120),
      width: 500,
      height: 400,
      z: zIndexRef.current++,
    });
  }, []);

  const handleClose = useCallback(() => {
    setDetailWidget(null);
  }, []);

  const handleMove = useCallback((x: number, y: number) => {
    setDetailWidget(prev => prev ? { ...prev, x, y } : null);
  }, []);

  const handleResize = useCallback((width: number, height: number) => {
    setDetailWidget(prev => prev ? { ...prev, width, height } : null);
  }, []);

  const handleFocus = useCallback(() => {
    setDetailWidget(prev => prev ? { ...prev, z: zIndexRef.current++ } : null);
  }, []);

  return (
    <>
      <div className="flex-1 overflow-y-auto -mx-4">
        {newsItems.map((item) => (
          <div
            key={item.id}
            className="px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => handleNewsClick(item)}
          >
            <h4 className="text-sm font-semibold text-gray-900 mb-1 line-clamp-2">
              {item.headline}
            </h4>
            <p className="text-xs text-gray-600 line-clamp-2">
              {item.description}
            </p>
          </div>
        ))}
      </div>
      {detailWidget && (
        <NewsDetailWidgetWindow
          newsItem={detailWidget.newsItem}
          x={detailWidget.x}
          y={detailWidget.y}
          width={detailWidget.width}
          height={detailWidget.height}
          z={detailWidget.z}
          onMove={handleMove}
          onResize={handleResize}
          onClose={handleClose}
          onFocus={handleFocus}
        />
      )}
    </>
  );
}

export default NewsFeedWidget;


