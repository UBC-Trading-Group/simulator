import React, { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { useWebSocketContext } from "../../contexts/WebSocketContext";

interface Tick {
  time: number;
  price: number;
}

interface TickHistory {
  [ticker: string]: Tick[];
}

const LiveLineChart: React.FC = () => {
  const { prices, lastUpdated, isConnected } = useWebSocketContext();
  const [history, setHistory] = useState<TickHistory>({});
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  const maxPoints = 50;
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];
  
  // Initialize selected tickers when prices first arrive
  useEffect(() => {
    if (selectedTickers.length === 0 && Object.keys(prices).length > 0) {
      setSelectedTickers(Object.keys(prices));
    }
  }, [prices, selectedTickers.length]);

  // Update history when prices change
  useEffect(() => {
    if (!lastUpdated) return;

    const now = Date.now();

    setHistory(prev => {
      const newHistory: TickHistory = { ...prev };

      Object.entries(prices).forEach(([ticker, price]) => {
        // Skip if price is null or invalid
        if (price == null || isNaN(price)) {
          return;
        }

        const prevArr = newHistory[ticker] ?? [];
        const lastTick = prevArr[prevArr.length - 1];

        // Create new array (avoid in-place mutation)
        let updated = [...prevArr];

        if (!lastTick || lastTick.time !== now) {
          updated.push({ time: now, price });
        } else {
          // Overwrite last tick if same timestamp
          updated[updated.length - 1] = { time: now, price };
        }

        // Apply maxPoints properly
        if (updated.length > maxPoints) {
          updated = updated.slice(-maxPoints);
        }

        newHistory[ticker] = updated;
      });

      return newHistory;
    });
  }, [prices, lastUpdated]);

  const allTickers = Object.keys(history);
  const tickers = allTickers.filter(t => selectedTickers.includes(t));

  const seriesList = tickers.map((ticker, index) => ({
    name: ticker,
    type: "line",
    data: history[ticker]
      .filter(p => p.price != null && !isNaN(p.price))
      .map(p => [p.time, parseFloat(p.price.toFixed(3))]),
    smooth: false,
    lineStyle: { color: colors[index % colors.length], width: 2 },
    itemStyle: { color: colors[index % colors.length] },
    symbol: "square",
    symbolSize: 3,
  }));

  const toggleTicker = (ticker: string) => {
    setSelectedTickers(prev => 
      prev.includes(ticker) 
        ? prev.filter(t => t !== ticker)
        : [...prev, ticker]
    );
  };

  const option = {
    tooltip: { 
      trigger: "axis", 
      order: "valueDesc",
      axisPointer: { type: "cross" },
    },
    legend: { 
      data: tickers, 
      top: 10,
      left: "center",
      textStyle: { fontSize: 12 }
    },
    grid: { left: "8%", right: "4%", bottom: "12%", top: "50px" },
    xAxis: { type: "time", boundaryGap: false },
    yAxis: { name: "Price ($)", scale: true },
    series: seriesList,
  };

  return (
    <div className="p-4 bg-white rounded-xl shadow-md" style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Stock selector */}
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: '8px', 
        marginBottom: '12px',
        padding: '8px',
        borderRadius: '8px',
        backgroundColor: '#f9fafb'
      }}>
        {allTickers.map((ticker, idx) => (
          <button
            key={ticker}
            onClick={() => toggleTicker(ticker)}
            style={{
              padding: '4px 12px',
              borderRadius: '6px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              backgroundColor: selectedTickers.includes(ticker) ? colors[idx % colors.length] : '#e5e7eb',
              color: selectedTickers.includes(ticker) ? 'white' : '#6b7280',
              transition: 'all 0.2s',
            }}
          >
            {ticker}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div style={{ flex: 1, minHeight: 0 }}>
        {tickers.length > 0 ? (
          <ReactECharts
            option={option}
            style={{ height: "100%", width: "100%" }}
            notMerge={true}
            lazyUpdate={true}
          />
        ) : (
          <div className="text-center py-4">
            {allTickers.length > 0 ? "Select stocks to display" : isConnected ? "Waiting for price updates..." : "Connecting to price..."}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveLineChart;
