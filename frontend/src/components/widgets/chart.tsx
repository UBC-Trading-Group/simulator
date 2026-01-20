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
  const maxPoints = 50;
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

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

  const tickers = Object.keys(history);

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

  const option = {
    title: { text: "Live Prices", left: "center" },
    tooltip: { 
      trigger: "axis", 
      order: "valueDesc",
      axisPointer: { type: "cross" },
    },
    legend: { data: tickers, top: 50, bottom: 50 },
    grid: { left: "10%", right: "10%", bottom: "15%", top: "15%" },
    xAxis: { type: "time", boundaryGap: false },
    yAxis: { name: "Price ($)", scale: true },
    series: seriesList,
  };

  return (
    <div className="p-4 bg-white rounded-xl shadow-md" style={{ height: '100%', width: '100%' }}>
      {tickers.length > 0 ? (
        <ReactECharts
          option={option}
          style={{ height: "100%", width: "100%" }}
          notMerge={true}
          lazyUpdate={true}
        />
      ) : (
        <div className="text-center py-4">
          {isConnected ? "Waiting for price updates..." : "Connecting to price..."}
        </div>
      )}
    </div>
  );
};

export default LiveLineChart;
